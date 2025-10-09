#!/usr/bin/env python3

"""This script simply wraps terragrunt (which is a wrapper around terraform...)
and its main function is to allow you to execute a `run-all` command but
broken up in individual steps.

This makes debugging a complex project easier, such as spotting where the
exact problem is.
"""

# pylint: disable=too-many-lines,too-many-arguments,too-many-positional-arguments
# pylint: disable=broad-exception-caught,broad-exception-raised

# idea: parse output
# - https://github.com/bcochofel/terraplanfeed/tree/main/terraplanfeed

import fnmatch
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import UTC, datetime

import click
import inquirer
import networkx as nx
import requests
import yaml

from .analyze import run_analyze
from .command_constructor import TgCommandConstructor
from .deploy import prepare_deploy_config, run_sync
from .inspector import AzureInspector
from .printer import Printer

STAGES = [
    "global",
    "sbx",
    "dev",
    "qas",
    "run",
    "tst",
    "acc",
    "prd",
]


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that serialises datetime objects as ISO strings."""

    def default(self, o):  # pylint: disable=arguments-renamed
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class TgWrap:
    """A wrapper around terragrunt with the sole purpose to make it a bit
    (in an opiionated way) easier to use
    """

    SEPARATOR = ":|:"
    VERSION_FILE = "version.hcl"
    LATEST_VERSION = "latest"
    PLANFILE_NAME = "planfile"
    TG_FILE = "terragrunt.hcl"
    TG_SOURCE_VAR = "TG_SOURCE"

    def __init__(self, verbose, check_tg_source=False):
        self.printer = Printer(verbose)

        # If needed, initialize the command constructor with the tg_source_indicator
        if check_tg_source:
            self.command_constructor = TgCommandConstructor(
                printer=self.printer, check_tg_source=check_tg_source
            )

    def _load_yaml_file(self, filepath):
        try:
            with open(filepath.strip(), encoding="utf-8") as file:
                return yaml.safe_load(file)
        except yaml.parser.ParserError:
            self.printer.error(
                f"Cannot parse YAML file {filepath}, check syntax please!"
            )
            sys.exit(1)

    def _check_directory_inclusion(
        self,
        directory,
        working_dir,
        exclude_external_dependencies,
        include_dirs=None,
        exclude_dirs=None,
    ):
        """Check whether a given directory should be included given a list of include and exclude glob patterns"""
        dir_excluded = False
        dir_included = (
            include_dirs is None or include_dirs == []
        )  # if we have a list of include dirs, then all others will be ignored
        dir_excluded_reason = ""

        # ensure consistency, remove possible trailing slashes from the dirs
        directory = directory.rstrip(os.path.sep)

        # ensure consistency, remove possible ./ prefixes from the dirs
        include_dirs = (
            [dir.lstrip(f".{os.path.sep}") for dir in include_dirs]
            if include_dirs
            else []
        )
        exclude_dirs = (
            [dir.lstrip(f".{os.path.sep}") for dir in exclude_dirs]
            if exclude_dirs
            else []
        )

        # Below doesn't seem to work, at least when using `analyze`
        # Not sure it has been added here in the first place

        # if the dir is not ending on '/*', add it
        # include_dirs = [dir.rstrip(f'.{os.path.sep}*') + f'{os.path.sep}*' for dir in include_dirs]
        # exclude_dirs = [dir.rstrip(f'.{os.path.sep}*') + f'{os.path.sep}*' for dir in exclude_dirs]

        common_path = os.path.commonpath(
            [os.path.abspath(working_dir), os.path.abspath(directory)]
        )
        self.printer.verbose(f"Common path for dir {directory}: {common_path}")

        if (
            common_path != os.path.abspath(working_dir)
            and exclude_external_dependencies
        ):
            dir_excluded = True
            dir_excluded_reason = "directory out of scope"
        else:
            for i in exclude_dirs:
                # Check direct match
                if fnmatch.fnmatch(directory, i):
                    dir_excluded = True
                    dir_excluded_reason = "directory explicitly excluded"
                # If pattern ends with /*, try several common variations
                elif i.endswith('/*'):
                    base_pattern = i[:-2]  # Remove /* -> **/dbx
                    wildcard_pattern = base_pattern + '*'  # Add * -> **/dbx*
                    if (fnmatch.fnmatch(directory, base_pattern) or
                        fnmatch.fnmatch(directory, wildcard_pattern)):
                        dir_excluded = True
                        dir_excluded_reason = "directory explicitly excluded"

            # if we have a specific set of include_dirs, then everything else should be excluded
            for i in include_dirs:
                # Check direct match
                if fnmatch.fnmatch(directory, i):
                    dir_included = True
                # If pattern ends with /*, try several common variations
                elif i.endswith('/*'):
                    base_pattern = i[:-2]  # Remove /* -> **/dbx
                    wildcard_pattern = base_pattern + '*'  # Add * -> **/dbx*
                    if (fnmatch.fnmatch(directory, base_pattern) or
                        fnmatch.fnmatch(directory, wildcard_pattern)):
                        dir_included = True

        if dir_excluded:  # directory explicitly excluded
            self.printer.verbose(
                f"- Remove directory '{directory}': {dir_excluded_reason}"
            )
        elif not dir_included:  # directory NOT explicitly excluded and NOT (no include dirs or not explicitly included)
            self.printer.verbose(
                f"- Remove directory '{directory}': specific list of include dirs given"
            )
        else:
            self.printer.verbose(f"+ Include directory: {directory}")

        return dir_included and not dir_excluded

    def _get_subdirectories_with_file(
        self,
        root_dir,
        file_name,
        exclude_external_dependencies,
        exclude_dirs=None,
        include_dirs=None,
        exclude_hidden_dir=True,
    ):
        # Get the current working directory
        current_dir = os.getcwd()
        # change to working directory, to avoid os.walk to include that in the paths
        os.chdir(root_dir)

        try:
            # ensure consistency, remove possible trailing slashes from the dirs
            exclude_dirs = (
                [dir.rstrip(os.path.sep) for dir in exclude_dirs]
                if exclude_dirs
                else []
            )
            include_dirs = (
                [dir.rstrip(os.path.sep) for dir in include_dirs]
                if include_dirs
                else []
            )

            subdirectories = []
            for directory, dirnames, filenames in os.walk("."):
                # Exclude hidden directories that start with a dot
                dirnames[:] = [
                    d
                    for d in dirnames
                    if not (d.startswith(".") and exclude_hidden_dir)
                ]

                # Check if the current directory contains the specified file
                if file_name in filenames:
                    self.printer.verbose(f"Directory found: {directory}")

                    include = self._check_directory_inclusion(
                        directory=directory.lstrip(f".{os.path.sep}"),
                        working_dir=".",
                        exclude_external_dependencies=exclude_external_dependencies,
                        include_dirs=include_dirs,
                        exclude_dirs=exclude_dirs,
                    )

                    if include:
                        subdirectories.append(directory.lstrip(f".{os.path.sep}"))

        finally:
            os.chdir(current_dir)

        return subdirectories

    def _prepare_groups(
        self,
        graph,
        exclude_external_dependencies,
        working_dir,
        exclude_dirs=None,
        include_dirs=None,
    ):
        """Prepare the list of groups that will be executed"""
        working_dir = os.path.abspath(working_dir) if working_dir else os.getcwd()
        self.printer.verbose(f"Check for working dir: {working_dir}")

        # ensure consistency, remove possible trailing slashes from the dirs
        exclude_dirs = (
            [dir.rstrip(os.path.sep) for dir in exclude_dirs] if exclude_dirs else []
        )
        include_dirs = (
            [dir.rstrip(os.path.sep) for dir in include_dirs] if include_dirs else []
        )

        self.printer.verbose(f"Include dirs: {'; '.join(include_dirs)}")
        self.printer.verbose(f"Exclude dirs: {'; '.join(exclude_dirs)}")

        groups = []
        for group in nx.topological_generations(graph):
            try:
                group.remove(
                    "\\n"
                )  # terragrunt is adding this in some groups for whatever reason
            except ValueError:
                pass

            for idx, directory in enumerate(group):
                include = self._check_directory_inclusion(
                    directory=directory,
                    working_dir=working_dir,
                    exclude_external_dependencies=exclude_external_dependencies,
                    include_dirs=include_dirs,
                    exclude_dirs=exclude_dirs,
                )

                if not include:
                    group[idx] = None

            # remove the null values from the list
            group = list(filter(None, group))
            if len(group) > 0:
                groups.append(group)

        return groups

    def _get_di_graph(self, backwards=False, working_dir=None):
        """Gets the directed graph of terragrunt dependencies, and parse it into a graph object"""
        graph = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w+", prefix="tgwrap-", delete=True
            ) as temp_file:
                self.printer.verbose(
                    f"Opened temp file for graph collection: {temp_file.name}"
                )

                working_dir_stmt = (
                    f"--working-dir {working_dir}" if working_dir else ""
                )
                command = f"terragrunt dag graph --non-interactive {working_dir_stmt}"
                rc = subprocess.run(
                    shlex.split(command),
                    text=True,
                    stdout=temp_file,
                    check=True,
                )
                self.printer.verbose(rc)

                temp_file.flush()

                graph = nx.DiGraph(nx.nx_pydot.read_dot(temp_file.name))
                if not backwards:
                    # For regular operations the graph must be reversed
                    graph = graph.reverse()
                else:
                    self.printer.verbose("Graph will be interpreted backwards!")
        except TypeError as e:
            self.printer.error(
                "terragrunt has problems generating the graph, check the dependencies please!"
            )
            self.printer.error("once fixed, you can run 'tgwrap show-graph' to verify.")
            raise click.ClickException(e)
        except Exception as e:
            self.printer.error(e)
            raise click.ClickException(e)

        return graph

    def _clone_repo(self, repo, target_dir, version_tag=None, prompt_func=None):
        """Clones the repo, possibly a specific version, into a temp directory"""

        def get_tags(target_dir):
            # Run the git command to fetch tags
            cmd = "git fetch --tags"
            subprocess.run(
                shlex.split(cmd),
                check=True,
                cwd=target_dir,
                stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            )

            # Run the git command to get the list of tags
            cmd = "git tag -l --sort=-committerdate"
            result = subprocess.run(
                shlex.split(cmd),
                text=True,
                check=True,
                cwd=target_dir,
                stdout=subprocess.PIPE,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            )
            self.printer.verbose(rc)

            # Get the list of tags
            tags = result.stdout.strip().split("\n")
            # remove empty strings
            tags = [tag for tag in tags if tag != ""]

            tags.insert(0, self.LATEST_VERSION)

            return tags

        def check_version_tag(reference, working_dir):
            is_latest = reference == self.LATEST_VERSION
            is_branch = False
            is_tag = False

            if not is_latest:
                quiet_mode = "" if self.printer.print_verbose else "--quiet"

                # Check if the given reference is a tag
                tag_command = (
                    f"git show-ref --verify {quiet_mode} refs/tags/{reference}"
                )
                tag_process = subprocess.run(
                    shlex.split(tag_command),
                    cwd=working_dir,
                    capture_output=True,
                    check=False,
                )
                is_tag = tag_process.returncode == 0
                self.printer.verbose(f"Check for tag: {tag_process}")

                # if it is not a tag, then it might be a branch
                if not is_tag:
                    branch_command = f"git switch {reference}"
                    branch_process = subprocess.run(
                        shlex.split(branch_command),
                        cwd=working_dir,
                        capture_output=True,
                        check=False,
                    )
                    is_branch = branch_process.returncode == 0
                    self.printer.verbose(f"Check for branch: {branch_process}")

            # Print the result
            if is_latest:
                self.printer.verbose(
                    f"The given reference '{reference}' is the latest version."
                )
            elif is_branch:
                self.printer.verbose(f"The given reference '{reference}' is a branch.")
            elif is_tag:
                self.printer.verbose(f"The given reference '{reference}' is a tag.")
            else:
                msg = f"The given reference '{reference}' is neither latest, a branch nor a tag."
                self.printer.verbose(msg)
                raise Exception(msg)

            return is_latest, is_branch, is_tag

        # clone the repo
        self.printer.verbose(f"Clone repo {repo}")
        cmd = f"git clone {repo} {target_dir}"
        rc = subprocess.run(
            shlex.split(cmd),
            check=True,
            stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
            stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
        )
        self.printer.verbose(rc)

        # if we don't have a version number specified, get them and let the user pick one
        if not version_tag:
            tags = get_tags(target_dir)
            questions = [
                inquirer.List(
                    "version",
                    message="Which version do you want to deploy?",
                    choices=tags,
                ),
            ]
            if prompt_func:
                version_tag = prompt_func(questions)["version"]
            else:
                version_tag = inquirer.prompt(questions)["version"]

            self.printer.normal("")

        # first check if we have a tag or a branch
        is_latest, is_branch, is_tag = check_version_tag(
            reference=version_tag,
            working_dir=target_dir,
        )

        self.printer.header(f"Fetch repo using reference {version_tag}")

        if is_latest:
            pass  # nothing to do, we already have latest
        elif is_tag:
            cmd = f"git checkout -b source {version_tag}"
            rc = subprocess.run(
                shlex.split(cmd),
                cwd=target_dir,
                check=True,
                stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            )
            self.printer.verbose(rc)
        elif is_branch:
            pass  # should already be present
        else:
            self.printer.error(
                f"Version tag {version_tag} seems neither a branch or a tag, cannot switch to it!"
            )

        return version_tag, is_branch, is_tag

    def _analyze_results(self, rc, messages):
        """Checks for errors"""
        error = False
        skip = False

        messages = messages.lower()

        if rc.returncode != 0 or "error" in messages.lower():
            error = True

        if "skipping terragrunt module" in messages.lower():
            skip = True

        return error, skip

    def _run_graph_step(
        self,
        command,
        working_dir,
        add_to_workdir,
        unit,
        collect_output_file,
        progress,
        output_queue=None,
        semaphore=None,
    ):
        """Runs a step in the graph"""
        unit_identifier = f"{unit}{self.SEPARATOR}"

        stop_processing = False
        error = False
        skip = False
        output = None
        error_msg = None
        messages = ""

        try:
            # if we are in multi-threading mode, acquire a semaphore
            if semaphore:
                semaphore.acquire()

            # if we have a specific working dir, and the dir is relative, combine the two
            if working_dir and not os.path.isabs(unit):
                working_dir = os.path.join(os.path.abspath(working_dir), unit)
            else:
                working_dir = unit

            if add_to_workdir:
                working_dir = os.path.join(working_dir, add_to_workdir)

            self.printer.verbose(
                f"Execute command: {command} in working dir: {working_dir}"
            )

            self.printer.header(
                f"\n\nStart processing unit: {unit} ({progress})\n\n",
                print_line_before=True,
            )

            if collect_output_file:
                self.printer.verbose("Use an output file for output collection")

                # unit identifier needs to be pre-written to output file, so that the output can be appended to it
                collect_output_file.write(unit_identifier)
                collect_output_file.flush()
            elif output_queue:
                self.printer.verbose("Use an output queue for output collection")

                # no output file, but data must be written to queue
                # so we need to capture the output
                collect_output_file = subprocess.PIPE

            messages = ""

            # planfile = os.path.join(working_dir, self.PLANFILE_NAME)
            # if f"--json {self.PLANFILE_NAME}" in command and not os.path.exists(planfile):
            #     skip = True
            #     output = '\n'
            #     self.printer.verbose(f"Planfile '{planfile}' does not exist")
            if os.path.exists(working_dir):
                with tempfile.NamedTemporaryFile(
                    mode="w+", prefix="tgwrap-", delete=False
                ) as f:
                    self.printer.verbose(
                        f"Opened temp file for error collection: {f.name}"
                    )
                    rc = {"returncode": 0}
                    rc = subprocess.run(
                        shlex.split(command),
                        text=True,
                        cwd=working_dir,
                        stdout=collect_output_file
                        if collect_output_file
                        else sys.stdout,
                        stderr=f,
                        check=False,
                    )
                    self.printer.verbose(f"arguments: {rc.args}")
                    self.printer.verbose(f"returncode: {rc.returncode}")
                    try:
                        self.printer.verbose(f"stdout: {rc.stdout[:200]}")
                    except Exception:
                        pass

                with open(f.name, encoding="utf-8") as f:
                    messages = f.read()

                error, skip = self._analyze_results(
                    rc=rc,
                    messages=messages,
                )

                # if we have a skipped module, and are collecting output, make sure we end up on a new line

                output = rc.stdout if rc.stdout else "\n"
            else:
                skip = True
                output = "\n"
                self.printer.verbose(f"Directory '{working_dir}' does not exist")

            if skip:
                self.printer.verbose("Module is skipped")

            if error:
                raise Exception(
                    f"An error situation detected while processing the terragrunt dependencies graph in directory {unit}"
                )
            self.printer.success(
                f"Directory {unit} processed successfully",
            )

        except FileNotFoundError:
            error_msg = f"Directory {working_dir} not found, continue"
            self.printer.warning(error_msg)
        except Exception as e:
            error_msg = f"Error occurred:\n{str(e)}"
            self.printer.error(error_msg)
            self.printer.error("Full stack:", print_line_before=True)
            self.printer.normal(messages, print_line_after=True)
            self.printer.normal(f"Directory {unit} failed!")

            stop_processing = True
        finally:
            if error_msg:
                output = json.dumps({"exception": error_msg})

            try:
                # communicate the results if desired
                if output_queue:
                    output_queue.put(f"{unit_identifier}{output}")
                elif collect_output_file and (skip or error):
                    collect_output_file.write(output)
                    collect_output_file.flush()
            except Exception as e:
                self.printer.error(f"Error writing the results: {e}")

            if semaphore:
                semaphore.release()
            try:
                os.remove(f.name)
            except Exception:
                pass

        return stop_processing

    def _run_di_graph(
        self,
        command,
        queue_exclude_external,
        start_at_step,
        ask_for_confirmation=False,
        collect_output_file=None,
        backwards=False,
        working_dir=None,
        include_dirs=None,
        exclude_dirs=None,
        use_native_terraform=False,
        add_to_workdir=None,
        continue_on_error=False,
    ):
        # Runs the desired command in the directories as defined in the directed graph
        if use_native_terraform:
            module_dirs = self._get_subdirectories_with_file(
                root_dir=working_dir if working_dir else ".",
                file_name=self.TG_FILE,
                exclude_hidden_dir=True,
                exclude_external_dependencies=queue_exclude_external,
                include_dirs=include_dirs,
                exclude_dirs=exclude_dirs,
            )
            # for native terraform, we just have one group with no inter-dependencies
            groups = [module_dirs]
        else:
            graph = self._get_di_graph(backwards=backwards, working_dir=working_dir)

            # first go through the groups and clean up where needed
            groups = self._prepare_groups(
                graph=graph,
                exclude_external_dependencies=queue_exclude_external,
                working_dir=working_dir,
                include_dirs=include_dirs,
                exclude_dirs=exclude_dirs,
            )

        if not groups:
            self.printer.error("No groups to process, this smells fishy!")
        elif ask_for_confirmation or self.printer.verbose:
            self.printer.header(
                "The following groups will be processed (sequentially):"
            )
            for idx, group in enumerate(groups):
                self.printer.normal(f"\nGroup {idx+1}:")
                for module in group:
                    self.printer.normal(f"- {module}")

        if ask_for_confirmation:
            response = input("\nDo you want to continue? (y/N) ")
            if response.lower() != "y":
                sys.exit(1)

        counter = 0
        nbr_of_groups = len(groups)
        for idx, group in enumerate(groups):
            group_nbr = idx + 1
            self.printer.header(f"Group {group_nbr}")
            self.printer.verbose(group)

            nbr_of_modules = len(group)
            for idx2, module in enumerate(group):
                counter += 1
                module_nbr = idx2 + 1
                progress = f"module {module_nbr} (of {nbr_of_modules}) of group {group_nbr} (of {nbr_of_groups})"

                step_nbr = group_nbr + module_nbr / 100
                if step_nbr < start_at_step:
                    self.printer.normal(
                        f"Skip step {step_nbr}, start at {start_at_step}"
                    )
                    continue

                stop_processing = self._run_graph_step(
                    command=command,
                    working_dir=working_dir,
                    add_to_workdir=add_to_workdir,
                    unit=module,
                    collect_output_file=collect_output_file,
                    progress=progress,
                )

                if stop_processing and not continue_on_error:
                    self.printer.warning(
                        f"Processing needs to be stopped at step {step_nbr}."
                    )
                    self.printer.normal(
                        f"After you've fixed the problem, you can continue where you left off by adding '--start-at-step {step_nbr}'."
                    )
                    sys.exit(1)

        if self.printer.print_verbose:
            total_items = sum(len(group) for group in groups)
            self.printer.verbose(f"Executed {group_nbr} groups and {total_items} steps")

    def _get_access_token(self):
        """Retrieve an access token"""
        #
        # Everything we do here, can be done using native python. And probably this is preferable as well.
        # But I have decided to follow (at least for now) the overall approach of the app and that is
        # executing systems commands.
        # This does require the az cli to be installed, but that is a fair assumption if you are working
        # with terragrunt/terraform and want to post the analyze results to an Azure Data Collection Endpoint.
        # However, not ruling out this will change, but then the change should be transparant.
        #

        # Get the Azure information
        rc = subprocess.run(
            shlex.split("az account show"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        self.printer.verbose(rc)

        # Do a few checks
        if rc.returncode != 0:
            raise Exception("Could not get Azure account info")

        # Get the ouptut
        output = json.loads(rc.stdout.decode())
        if output.get("environmentName") != "AzureCloud":
            raise Exception(
                f"Environment is not an Azure cloud:\n{json.dumps(output, indent=2)}"
            )

        tenant_id = output.get("tenantId")
        if not tenant_id:
            raise Exception(
                f"Could not determine Azure tenant id:\n{json.dumps(output, indent=2)}"
            )

        principal = output.get("user").get("name")
        if not principal:
            raise Exception(
                f"Could not determine principal:\n{json.dumps(output, indent=2)}"
            )

        # TOKEN=$(az account get-access-token --scope "https://monitor.azure.com//.default" | jq -r '.accessToken')
        # Get the Azure OAUTH token
        rc = subprocess.run(
            shlex.split(
                'az account get-access-token --scope "https://monitor.azure.com//.default"'
            ),
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        self.printer.verbose(rc.returncode)  # do not print the token to output

        # Do a few checks
        if rc.returncode != 0:
            raise Exception("Could not get Azure OAUTH token")

        # Get the ouptut
        output = json.loads(rc.stdout.decode())
        token = output.get("accessToken")
        if not token:
            raise Exception(
                f"Could not retrieve an access token:\n{json.dumps(output, indent=2)}"
            )

        return principal, token

    def _post_to_dce(self, data_collection_endpoint, payload, token=None):
        if not token:
            _, token = self._get_access_token()

        # DCE payload must be submitted as an arry
        if not isinstance(payload, list):
            dce_payload = [payload]
        else:
            dce_payload = payload

        self.printer.verbose("About to log:")
        self.printer.verbose(f"- to: {data_collection_endpoint}")
        self.printer.verbose(f"- payload:\n{json.dumps(dce_payload, indent=2)}")

        # now do the actual post
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                url=data_collection_endpoint,
                headers=headers,
                json=dce_payload,
                timeout=10,
            )

            resp.raise_for_status()
            self.printer.success(
                "Analyze results logged to DCE", print_line_before=True
            )

        except requests.exceptions.RequestException as e:
            # we warn but continue
            self.printer.warning(
                f"Error while posting the analyze results ({type(e)}): {e}",
                print_line_before=True,
            )
        except Exception as e:
            self.printer.error(f"Unexpected error: {e}")
            if self.printer.print_verbose:
                raise e
            sys.exit(1)

    def _post_analyze_results_to_dce(
        self, data_collection_endpoint: str, payload: object
    ):
        """Posts the payload to the given (Azure) data collection endpoint"""

        def mask_basic_auth(url):
            # Regular expression to match basic authentication credentials in URL
            auth_pattern = re.compile(r"(https?://)([^:@]+):([^:@]+)@(.+)")
            # Return the url without the basic auth part
            return auth_pattern.sub(r"\1\4", url)

        principal, token = self._get_access_token()

        # Get the repo info
        rc = subprocess.run(
            shlex.split("git config --get remote.origin.url"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        self.printer.verbose(rc)

        # Do a few checks
        if rc.returncode != 0:
            raise Exception("Could not get git repo info")

        # Get the ouptut
        repo = rc.stdout.decode().rstrip("\n")
        if not repo:
            raise Exception(f"Could not get git repo info: {repo}")

        # Remove the basic auth info if it is part of the url
        repo = mask_basic_auth(repo)

        # Get the current path in the repo
        rc = subprocess.run(
            shlex.split("git rev-parse --show-prefix"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        self.printer.verbose(rc)

        # Do a few checks
        if rc.returncode != 0:
            raise Exception("Could not get current scope")

        # Get the ouptut
        scope = rc.stdout.decode().rstrip("\n")
        if not scope:
            raise Exception(f"Could not get scope: {scope}")

        # So now we have everything, we can construct the final payload
        payload = {
            "scope": scope,
            "principal": principal,
            "repo": repo,
            "creations": payload.get("summary").get("creations"),
            "updates": payload.get("summary").get("updates"),
            "deletions": payload.get("summary").get("deletions"),
            "minor": payload.get("summary").get("minor"),
            "medium": payload.get("summary").get("medium"),
            "major": payload.get("summary").get("major"),
            "unknown": payload.get("summary").get("unknown"),
            "total": payload.get("summary").get("total"),
            "score": payload.get("summary").get("score"),
            "details": payload.get("details"),
        }
        self._post_to_dce(
            payload=payload,
            data_collection_endpoint=data_collection_endpoint,
            token=token,
        )

        self.printer.verbose("Done")

    def _show_version(self, working_dir):
        """Show the version information of the tools"""
        self.printer.header("Version info")
        for cmd in ["terragrunt --version", "tf --version", "tgwrap --version"]:
            cmd_args = shlex.split(cmd)
            try:
                rc = subprocess.run(
                    cmd_args,
                    check=True,
                    stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                    stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
                    cwd=working_dir if working_dir else None,
                )
                self.printer.verbose(rc)
            except FileNotFoundError:
                self.printer.warning(
                    f"Command '{cmd_args[0]}' not found on PATH, skipping version check."
                )

    def _is_external_dependency(self, directory, working_dir):
        """Determine if a directory is an external dependency (outside the working dir)."""
        try:
            abs_working_dir = os.path.abspath(working_dir)
            abs_directory = os.path.abspath(directory)
            return not abs_directory.startswith(abs_working_dir)
        except Exception:
            return False

    def run(
        self,
        command: str,
        debug: bool,
        no_lock: bool,
        update: bool,
        upgrade: bool,
        planfile: bool,
        auto_approve: bool,
        all: bool,
        clean: bool,
        working_dir: str,
        queue_exclude_external: bool,
        step_by_step: bool,
        continue_on_error: bool,
        start_at_step: float,
        include_dirs: list[str],
        exclude_dirs: list[str],
        analyze_after_plan: bool,
        analyze_config: bool,
        ignore_attributes: list[str],
        planfile_dir: str,
        data_collection_endpoint: str,
        terragrunt_args: list[str],
    ):  # pylint: disable=redefined-builtin
        """Executes a terragrunt command across multiple modules"""
        self.printer.verbose(f"Attempting to execute 'run-all {command}'")
        if terragrunt_args:
            self.printer.verbose(
                f"- with additional parameters: {' '.join(terragrunt_args)}"
            )

        if self.printer.print_verbose:
            self._show_version(working_dir=working_dir)

        if not all and not step_by_step:
            check_for_file = self.TG_FILE
            if working_dir:
                check_for_file = os.path.join(working_dir, check_for_file)

            if not os.path.isfile(check_for_file):
                self.printer.error(
                    f"{check_for_file} not found, this seems not to be a terragrunt module directory!"
                )
                sys.exit(1)

        # auto approve is only relevant with a modifying command
        modifying_command = command.lower() in ["apply", "destroy"]
        auto_approve = auto_approve if modifying_command else True

        cmd = self.command_constructor.construct_command(
            command=command,
            debug=debug,
            queue_exclude_external=True if step_by_step else queue_exclude_external,
            all=all,
            step_by_step=step_by_step,
            non_interactive=True if step_by_step else auto_approve,
            no_auto_approve=False if step_by_step else (not auto_approve),
            no_lock=no_lock,
            update=update,
            upgrade=upgrade,
            planfile=planfile,
            working_dir=None if step_by_step else working_dir,
            include_dirs=[] if step_by_step else include_dirs,
            exclude_dirs=[] if step_by_step else exclude_dirs,
            terragrunt_args=terragrunt_args,
        )

        if clean:
            self.clean(working_dir=working_dir)

        rc = None
        if step_by_step:
            self.printer.verbose(
                f"This command will be executed for each individual module:\n$ {cmd}"
            )

            # if the dir is not ending on '/*', add it
            include_dirs = [
                dir.rstrip(f".{os.path.sep}*") + f"{os.path.sep}*"
                for dir in include_dirs
            ]
            exclude_dirs = [
                dir.rstrip(f".{os.path.sep}*") + f"{os.path.sep}*"
                for dir in exclude_dirs
            ]

            self._run_di_graph(
                command=cmd,
                queue_exclude_external=queue_exclude_external,
                working_dir=working_dir,
                ask_for_confirmation=(not auto_approve),
                continue_on_error=continue_on_error,
                start_at_step=start_at_step,
                backwards=(command.lower() in ["destroy"]),
                include_dirs=include_dirs,
                exclude_dirs=exclude_dirs,
            )
        else:
            rc = subprocess.run(shlex.split(cmd), check=False)

            self.printer.verbose(rc)

        # If we don't requrest specifically to analyze after plan, we do it only in --all mode
        analyze_after_plan = all if analyze_after_plan is None else analyze_after_plan

        if not rc:  # this happens in step by step mode
            pass
        elif rc.returncode != 0:
            self.printer.error(
                f"An error occurred (return code {rc.returncode}) while executing command: {command.lower()}"
            )
            self.printer.verbose(f"Executed command: {json.dumps(rc.args, indent=2)}")
        elif analyze_after_plan and command.lower() == "plan":
            self.printer.verbose("Analyze after plan requested")
            self.analyze(
                queue_exclude_external=queue_exclude_external,
                working_dir=working_dir,
                start_at_step=0,
                out=None,
                analyze_config=analyze_config,
                ignore_attributes=ignore_attributes,
                include_dirs=include_dirs,
                exclude_dirs=exclude_dirs,
                planfile_dir=planfile_dir,
                data_collection_endpoint=data_collection_endpoint,
                terragrunt_args=terragrunt_args,
            )

        if rc:
            sys.exit(rc.returncode)

    def analyze(
        self,
        queue_exclude_external,
        working_dir,
        start_at_step,
        out,
        analyze_config,
        ignore_attributes,
        include_dirs,
        exclude_dirs,
        planfile_dir,
        data_collection_endpoint,
        terragrunt_args,
    ):
        """Analyzes the plan files"""

        def calculate_score(major: int, medium: int, minor: int) -> float:
            return major * 10 + medium + minor / 10

        self.printer.verbose("Attempting to 'analyze'")
        if terragrunt_args:
            self.printer.verbose(
                f"- with additional parameters: {' '.join(terragrunt_args)}"
            )

        # determine whether we are going to use a native 'tf show' (which is much faster!) or need
        # to use a terragrunt show
        if start_at_step > 1 or not queue_exclude_external or not planfile_dir:
            if self.printer.print_verbose:
                self.printer.warning(
                    "Use terragrunt for module selection, this will be significantly slower!"
                )

            use_native_tf = False

            # some environments raise the error: AttributeError: ‘tuple’ object has no attribute ‘append’
            # so convert to a list to make it updateable
            tg_args_list = list(terragrunt_args)

            # first run a 'show' and write output to file
            if not any(arg in ["--json", "-json"] for arg in tg_args_list):
                tg_args_list.append("--json")

            if self.PLANFILE_NAME not in tg_args_list:
                tg_args_list.append(self.PLANFILE_NAME)

            cmd = self.command_constructor.construct_command(
                command="show",
                debug=False,
                queue_exclude_external=queue_exclude_external,
                terragrunt_args=tg_args_list,
            )
        else:
            if self.printer.print_verbose:
                self.printer.success(
                    "Use native tofu|terraform (by using tf alias) for module selection"
                )

            use_native_tf = True
            # the 'tf' command is part of tenv and determines, based on the existence of .opentofu-version or .terraform-version
            # whether to use terraform or opentofu
            cmd = f"tf show --json {self.PLANFILE_NAME}"

        config = None
        if analyze_config:
            self.printer.verbose(f"\nAnalyze using config {analyze_config}")
            config = self._load_yaml_file(analyze_config)

        ts_validation_successful = True
        details = {}
        try:
            # then run it and capture the output
            with tempfile.NamedTemporaryFile(
                mode="w+", prefix="tgwrap-", delete=False
            ) as f:
                self.printer.verbose(
                    f"Opened temp file for output collection: {f.name}"
                )

                self._run_di_graph(
                    command=cmd,
                    queue_exclude_external=queue_exclude_external,
                    collect_output_file=f,
                    working_dir=working_dir,
                    start_at_step=start_at_step,
                    ask_for_confirmation=False,
                    include_dirs=include_dirs,
                    exclude_dirs=exclude_dirs,
                    use_native_terraform=use_native_tf,
                    add_to_workdir=planfile_dir if use_native_tf else None,
                )

            with open(f.name, encoding="utf-8") as f:
                for line in f:
                    split_line = line.split(self.SEPARATOR)
                    module = split_line[0]

                    try:
                        plan_file = split_line[1]
                    except IndexError:
                        self.printer.warning(
                            f"Could not determine planfile: {line[:100]}"
                        )

                    try:
                        # plan file could be empty (except for new line) if module is skipped
                        if len(plan_file) > 1:
                            data = json.loads(plan_file)

                            # do we have an exception logged?
                            if "exception" in data:
                                raise Exception(data["exception"])

                            details[module], ts_success = run_analyze(
                                config=config,
                                data=data,
                                verbose=self.printer.print_verbose,
                                ignore_attributes=ignore_attributes,
                            )

                            if not ts_success:
                                ts_validation_successful = False
                        else:
                            self.printer.warning(
                                f"Planfile for module {module} is empty"
                            )
                    except json.decoder.JSONDecodeError as e:
                        raise Exception(
                            "Exception detected or planfile for "
                            f"{module} was not proper json, further analysis not "
                            f"possible:\n{plan_file[:200]}"
                        ) from e
        finally:
            os.remove(f.name)

        # calulate the total drifts and scoe
        total_drifts = {
            "creations": 0,
            "updates": 0,
            "deletions": 0,
            "outputs": 0,
            "minor": 0,
            "medium": 0,
            "major": 0,
            "unknown": 0,
            "total": 0,
            "score": 0,
        }

        self.printer.header("Analysis results:", print_line_before=True)
        for key, value in details.items():
            # if we want to ignore a few attributes
            if ignore_attributes:
                value["updates"] = [
                    item
                    for item in value["updates"]
                    if item not in value["ignorable_updates"]
                ]

            self.printer.header(f"Module: {key}")
            if not value["all"] and not value["outputs"]:
                self.printer.success("No changes detected")

            if value["unauthorized"]:
                self.printer.error("Unauthorized deletions:")
                for m in value["unauthorized"]:
                    self.printer.error(f"-> {m}")
            if value["deletions"]:
                self.printer.warning("Deletions:")
                for m in value["deletions"]:
                    total_drifts["deletions"] = total_drifts["deletions"] + 1
                    self.printer.warning(f"-> {m}")
            if value["creations"]:
                self.printer.normal("Creations:")
                for m in value["creations"]:
                    total_drifts["creations"] = total_drifts["creations"] + 1
                    self.printer.normal(f"-> {m}")
            if value["updates"]:
                self.printer.normal("Updates:")
                for m in value["updates"]:
                    total_drifts["updates"] = total_drifts["updates"] + 1
                    self.printer.normal(f"-> {m}")
            if value["ignorable_updates"]:
                if self.printer.print_verbose:
                    self.printer.normal("Updates (ignored):")
                    for m in value["ignorable_updates"]:
                        self.printer.normal(f"-> {m}")
                else:
                    self.printer.normal(
                        f'Updates (ignored): {len(value["ignorable_updates"])} resources (add --verbose to see them)'
                    )
            if value["outputs"]:
                self.printer.normal("Output changes:")
                for m in value["outputs"]:
                    total_drifts["outputs"] = total_drifts["outputs"] + 1
                    self.printer.normal(f"-> {m}")

        if not analyze_config:
            self.printer.error(
                "Analyze config file is not set, this is required for checking for unauthorized deletions and drift detection scores!",
                print_line_before=True,
            )
        else:
            for key, value in details.items():
                for drift_type in ["minor", "medium", "major", "unknown", "total"]:
                    total_drifts[drift_type] += value["drifts"][drift_type]

                # the formula below is just a way to achieve a numeric results that is coming from the various drift categories
                value["drifts"]["score"] = calculate_score(
                    major=value["drifts"]["major"],
                    medium=value["drifts"]["medium"],
                    minor=value["drifts"]["minor"],
                )
                value["drifts"]["score"] = (
                    value["drifts"]["major"] * 10
                    + value["drifts"]["medium"]
                    + value["drifts"]["minor"] / 10
                )

            # the formula below is just a way to achieve a numeric results that is coming from the various drift categories
            total_drift_score = (
                total_drifts["major"] * 10
                + total_drifts["medium"]
                + total_drifts["minor"] / 10
            )
            total_drifts["score"] = total_drift_score

            self.printer.header(
                f"Drift score: {total_drift_score} ({total_drifts['major']}.{total_drifts['medium']}.{total_drifts['minor']})"
            )
            if total_drifts["unknown"] > 0:
                self.printer.warning(
                    f"For {total_drifts['unknown']} resources, drift score is not configured, please update configuration!"
                )
                self.printer.warning("- Unknowns:")
                for key, value in details.items():
                    for m in value["unknowns"]:
                        self.printer.warning(f" -> {m}")

        if out or data_collection_endpoint:
            # in the output we convert the dict of dicts to a list of dicts as it makes processing
            # (e.g. by telegraph) easier.
            output = {
                "details": [],
                "summary": {},
            }
            for key, value in details.items():
                value["module"] = key
                output["details"].append(value)

            output["summary"] = total_drifts

            if out:
                print(json.dumps(output, indent=4))

            if data_collection_endpoint:
                self._post_analyze_results_to_dce(
                    data_collection_endpoint=data_collection_endpoint,
                    payload=output,
                )

        if not ts_validation_successful:
            self.printer.error(
                "Analysis detected unauthorised deletions, please check your configuration!!!"
            )
            sys.exit(1)

    def sync(
        self,
        source_stage,
        target_stage,
        source_domain,
        target_domain,
        module,
        auto_approve,
        clean,
        include_dotenv_file,
        working_dir,
    ):
        """Syncs the terragrunt config files from one stage to another (and possibly to a different domain)"""
        if target_domain and not source_domain:
            raise Exception(
                "Providing a target domain while omitting the source domain is not supported!"
            )
        if source_domain and not target_domain:
            raise Exception(
                "Providing a source domain while omitting the target domain is not supported!"
            )

        if target_domain and not target_stage:
            self.printer.verbose(
                "No target stage given, assume the same as source stage"
            )
            target_stage = source_stage

        if not source_domain and not target_domain and not target_stage:
            raise Exception(
                "When not providing domains, you need to provide a target stage!"
            )

        # do we have a working dir?
        working_dir = working_dir if working_dir else os.getcwd()
        # the domains will be ignored when omitted as input
        source_path = os.path.join(working_dir, source_domain, source_stage, module, "")
        target_path = os.path.join(working_dir, target_domain, target_stage, module, "")

        run_sync(
            source_path=source_path,
            target_path=target_path,
            source_domain=source_domain,
            source_stage=source_stage,
            target_stage=target_stage,
            include_dotenv_file=include_dotenv_file,
            auto_approve=auto_approve,
            clean=clean,
            terragrunt_file=self.TG_FILE,
            verbose=self.printer.print_verbose,
        )

    def sync_dir(
        self,
        source_directory,
        target_directory,
        auto_approve,
        clean,
        include_dotenv_file,
        working_dir,
    ):
        """Syncs the terragrunt config files from one directory to anothery"""
        # do we have a working dir?
        working_dir = working_dir if working_dir else os.getcwd()
        # the domains will be ignored when omitted as input
        source_path = os.path.join(working_dir, source_directory, "")
        target_path = os.path.join(working_dir, target_directory, "")

        run_sync(
            source_path=source_path,
            target_path=target_path,
            auto_approve=auto_approve,
            clean=clean,
            include_dotenv_file=include_dotenv_file,
            terragrunt_file=self.TG_FILE,
            verbose=self.printer.print_verbose,
        )

    def deploy(
        self,
        manifest_file,
        version_tag,
        target_stages,
        include_global_config_files,
        auto_approve,
        working_dir,
    ):
        """Deploys the terragrunt config files from a git repository"""
        try:
            temp_dir = os.path.join(tempfile.mkdtemp(prefix="tgwrap-"), "tg-source")

            # do we have a working dir?
            working_dir = working_dir if working_dir else os.getcwd()

            manifest = self._load_yaml_file(os.path.join(working_dir, manifest_file))

            source_dir = os.path.join(temp_dir, manifest["base_path"])

            # accept that the `config_path` is not set, only needed when deploying config files
            # and this will be checked later (if applicable)
            try:
                source_config_dir = os.path.join(temp_dir, manifest["config_path"])
            except KeyError:
                source_config_dir = None

            version_tag, _, _ = self._clone_repo(
                repo=manifest["git_repository"],
                target_dir=temp_dir,
                version_tag=version_tag,
            )

            # collect all the base paths of the substacks as you don't want
            # to include them in regular syncs, add some standard paths there by default
            substacks = ["substacks", "sub_stacks"]
            for _, substack in manifest.get("sub_stacks", {}).items():
                # get the base directory of the sub stack so that we can ignore it when deploying the regular modules
                substacks.append(substack["source"].split(os.path.sep)[0])

            # and make it unique
            substacks = set(substacks)

            # the manifest file supports both `sub_stacks` and `substack` config
            # names. Annoying to be a bit autistic when it comes to naming :-/
            substack_configs = manifest.get("sub_stacks", {})
            substack_configs.update(manifest.get("substacks", {}))

            for target_stage in target_stages:
                target_dir = os.path.join(working_dir, "", target_stage)
                self.printer.header(f"Deploy stage {target_stage} to {target_dir}...")
                try:
                    os.makedirs(target_dir)
                except FileExistsError:
                    pass

                deploy_actions = {}
                deploy_global_configs = include_global_config_files
                target_stage_found = False
                # now go through the deploy configurations and apply the one that is relevant
                for key, value in manifest["deploy"].items():
                    if target_stage not in value["applies_to_stages"]:
                        self.printer.verbose(
                            f"Target stage {target_stage} not applicable for action {key}."
                        )
                    else:
                        deploy_actions.update(
                            prepare_deploy_config(
                                step=key,
                                config=value,
                                source_dir=source_dir,
                                source_config_dir=source_config_dir,
                                target_dir=target_dir,
                                target_stage=target_stage,
                                substacks=substacks,
                                substack_configs=substack_configs.items(),
                                tg_file_name=self.TG_FILE,
                                verbose=self.printer.print_verbose,
                            )
                        )
                        deploy_global_configs = value.get(
                            "include_global_config_files", deploy_global_configs
                        )
                        target_stage_found = True

                if target_stage_found and deploy_global_configs:
                    for gc, global_config in manifest.get(
                        "global_config_files", {}
                    ).items():
                        self.printer.verbose(f"Found global config : {gc}")

                        source_path = os.path.join(source_dir, global_config["source"])

                        target = global_config.get("target", global_config["source"])
                        target_path = os.path.dirname(
                            os.path.join(
                                working_dir,
                                target,
                            )
                        )
                        if os.path.exists(source_path):
                            deploy_actions[f"global configs -> {target}"] = {
                                "source": source_path,
                                "target": target_path,
                            }
                        else:
                            self.printer.warning(
                                f"Source path of global configs does not exist: {source_path}"
                            )
                else:
                    self.printer.verbose("Skipping global configs")

                if deploy_actions:
                    self.printer.header("Modules to deploy:")
                    self.printer.normal(
                        f'-> git repository: {manifest["git_repository"]}'
                    )
                    self.printer.normal(f"-> version tag: {version_tag}")
                    self.printer.normal("Modules:")
                    for key, value in deploy_actions.items():
                        self.printer.normal(f"--> {key}")

                    response = "n"
                    if not auto_approve:
                        response = input("\nDo you want to continue? (y/N) ")
                        # if response.lower() != "y":
                        #     sys.exit(1)

                    if auto_approve or response.lower() == "y":
                        for key, value in deploy_actions.items():
                            run_sync(
                                source_path=value["source"],
                                target_path=value["target"],
                                excludes=value.get("excludes", []),
                                include_dotenv_file=True,
                                auto_approve=True,
                                clean=False,
                                terragrunt_file=self.TG_FILE,
                                verbose=self.printer.print_verbose,
                            )

                        with open(
                            os.path.join(target_dir, self.VERSION_FILE), "w",
                            encoding="utf-8",
                        ) as f:
                            f.write(
                                f"""
locals {{
  version_tag="{version_tag}"
}}
"""
                            )
                else:
                    self.printer.normal("Nothing to do")

                # clean up the cache in the deployed directory to avoid strange issues when planning
                self.clean(working_dir=target_dir)

        except KeyError as e:
            self.printer.error(
                f"Error interpreting the manifest file. Please ensure it uses the proper format. Could not find element: {e}"
            )
            sys.exit(1)
        except Exception as e:
            self.printer.error(f"Unexpected error: {e}")
            if self.printer.print_verbose:
                raise e
            sys.exit(1)
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def check_deployments(self, repo_url, levels_deep, working_dir, out):
        """Check the freshness of deployed configuration versions against the platform repository"""

        def locate_version_files(
            current_directory,
            found_files=None,
            root_directory=None,
            level=1,
            git_status="",
        ):
            "This tries to find a version file in the current directory, or a given number of directories beneath it"
            found_files = found_files if found_files else []

            # do not include hidden directories
            if os.path.basename(current_directory).startswith("."):
                return found_files

            if not root_directory:
                root_directory = current_directory

            if not git_status:
                self.printer.verbose(
                    f"Check for git status in directory {current_directory}"
                )
                # Execute 'git status' to get an overview of the current status
                cmd = "git status"
                rc = subprocess.run(
                    shlex.split(cmd),
                    cwd=current_directory,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                output = ("stdout: " + rc.stdout + "stderr: " + rc.stderr).lower()
                if "not a git repository" in output:
                    pass
                elif "branch is up to date" in output:
                    git_status = "up to date; "
                elif "head detached" in output:
                    git_status = "head detached; "
                elif "untracked files" in output:
                    git_status = git_status + "untracked files; "
                elif "changes to be committed" in output:
                    git_status = git_status + "staged changes; "
                elif "changes not staged for commit" in output:
                    git_status = git_status + "unstaged changes; "
                elif "branch is ahead of" in output:
                    git_status = git_status + "ahead of remote; "
                elif "branch is behind of" in output:
                    git_status = git_status + "behind remote; "
                elif "unmerged paths" in output:
                    git_status = git_status + "merge conflicts; "

            for entry in os.listdir(current_directory):
                full_entry = os.path.join(current_directory, entry)

                if os.path.isdir(full_entry) and level <= levels_deep:
                    found_files = locate_version_files(
                        current_directory=full_entry,
                        found_files=found_files,
                        root_directory=root_directory,
                        level=level + 1,
                        git_status=git_status,
                    )
                elif entry == self.VERSION_FILE:
                    found_files.append(
                        {
                            "path": os.path.relpath(current_directory, root_directory),
                            "git_status": git_status,
                        }
                    )

            return found_files

        def get_all_versions(repo_dir, min_version=None):
            "Get all the version tags from the repo including their data"
            # Execute 'git tag' command to get a list of all tags
            cmd = "git tag --sort='-refname:short' --format='%(refname:short) %(creatordate:iso8601)'"
            output = subprocess.check_output(
                shlex.split(cmd),
                text=True,
                cwd=repo_dir,
                universal_newlines=True,
            )

            # Split the output into lines
            timestamp_format = "%Y-%m-%d %H:%M:%S %z"
            tags = {}
            lines = output.splitlines()
            for line in lines:
                tag_name, created_date = line.split(" ", maxsplit=1)
                tags[tag_name] = {
                    "created_date": datetime.strptime(created_date, timestamp_format)
                }

                if tag_name == min_version:
                    break

            self.printer.verbose(f"Found {len(tags)} tags: {tags}")

            return tags

        try:
            # do we have a working dir?
            working_dir = working_dir if working_dir else os.getcwd()
            self.printer.header(
                f"Check released versions (max {levels_deep} levels deep) in directory: {working_dir}"
            )

            found_files = locate_version_files(working_dir)

            versions = []
            for result in found_files:
                # Determine the deployed version as defined in the version file
                with open(
                    os.path.join(working_dir, result["path"], self.VERSION_FILE),
                    encoding="utf-8",
                ) as file:
                    content = file.read()
                    # Use regex to extract version_tag value from HCL file
                    version_match = re.search(
                        r'version_tag\s*=\s*["\']([^"\']+)["\']', content
                    )
                    if version_match:
                        version_tag = version_match.group(1)
                        versions.append(
                            {
                                "path": result["path"],
                                "git_status": result["git_status"],
                                "tag": version_tag,
                            }
                        )
                    else:
                        self.printer.warning(
                            f'Could not determine version tag in file {os.path.join(result["path"], self.VERSION_FILE)}'
                        )
                        versions.append({result["path"]: "unknown"})

            self.printer.verbose(f"Detected versions: {versions}")

            # remove the 'latest' tag from the detected versions, as it is specific one
            filtered_versions = list(
                filter(lambda x: x["tag"] != self.LATEST_VERSION, versions)
            )

            if filtered_versions:
                min_version = min(filtered_versions, key=lambda x: x["tag"])
                max_version = max(filtered_versions, key=lambda x: x["tag"])
            else:
                min_version = None
                max_version = None

            self.printer.verbose(
                f"Detected minimum version {min_version} and maximum version {max_version}"
            )

            temp_dir = os.path.join(tempfile.mkdtemp(prefix="tgwrap-"), "tg-source")
            self._clone_repo(
                repo=repo_url,
                target_dir=temp_dir,
                version_tag="latest",
            )

            # determine the version tag from the repo, including their date
            all_versions = get_all_versions(
                repo_dir=temp_dir, min_version=min_version["tag"]
            )

            # so now we can determine how old the deployed versions are
            now = datetime.now(UTC)
            for version in versions:
                tag = version["tag"]
                if tag == self.LATEST_VERSION:
                    version["release_date"] = "unknown"
                else:
                    release_date = all_versions[tag]["created_date"]
                    version["release_date"] = release_date
                    version["days_since_release"] = (now - release_date).days

            self.printer.header(
                "Deployed versions:"
                if len(versions) > 0
                else "No deployed versions detected",
                print_line_before=True,
            )

            # sort the list based on its path
            versions = sorted(versions, key=lambda x: x["path"])

            for version in versions:
                days_since_release = version.get("days_since_release", 0)
                message = f'-> {version["path"]}: {version["tag"]} (released {days_since_release} days ago)'
                if version["release_date"] == "unknown":
                    self.printer.normal(message)
                elif days_since_release > 120:
                    self.printer.error(message)
                elif days_since_release > 80:
                    self.printer.warning(message)
                elif days_since_release < 40:
                    self.printer.success(message)
                else:
                    self.printer.normal(message)

                if version.get("git_status"):
                    message = f'WARNING: git status: {version["git_status"].strip()}'
                    if "up to date" not in message:
                        self.printer.warning(message)

            self.printer.normal("\n")  # just to get an empty line :-/
            self.printer.warning(
                """
Note:
    This result only says something about the freshness of the deployed configurations,
    but not whether the actual resources are in sync with these.

    Check the drift of these configurations with the actual deployments by
    planning and analyzing the results.

    Also, it uses the locally checked out repositories, make sure these are pulled so that
    this reflect the most up to date situation!
            """,
                print_line_before=True,
                print_line_after=True,
            )

            if out:
                # use the regular printer, to avoid it being sent to stderr
                print(json.dumps(versions, indent=4, cls=DateTimeEncoder))

        except KeyError as e:
            self.printer.error(
                f"Error interpreting the manifest file. Please ensure it uses the proper format. Could not find element: {e}"
            )
            if self.printer.print_verbose:
                raise e
            sys.exit(1)
        except Exception as e:
            self.printer.error(f"Unexpected error: {e}")
            if self.printer.print_verbose:
                raise e
            sys.exit(1)
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def show_graph(
        self,
        backwards,
        exclude_external_dependencies,
        analyze,
        working_dir,
        include_dirs,
        exclude_dirs,
        terragrunt_args,
    ):
        """Shows the dependencies of a project"""

        def set_json_dumps_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        def calculate_dependencies(graph):
            dependencies = {}
            for node in graph.nodes:
                out_degree = graph.out_degree(node)
                in_degree = graph.in_degree(node)
                total_degree = out_degree + in_degree
                dependencies[node] = {
                    "dependencies": out_degree,
                    "dependent_on_it": in_degree,
                    "total": total_degree,
                }

            return dependencies

        def calculate_graph_metrics(graph):
            metrics = {}

            # Degree centrality
            metric = {
                "values": dict(
                    sorted(
                        nx.degree_centrality(graph).items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ),
                "description": "Shows the degree of each node relative to the number of nodes in the graph",
            }
            metrics["degree_centrality"] = metric

            # Betweenness centrality
            metric = {
                "values": dict(
                    sorted(
                        nx.betweenness_centrality(graph).items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ),
                "description": "Indicates nodes that frequently lie on shortest paths between other nodes",
            }
            metrics["betweenness_centrality"] = metric

            # Closeness centrality
            metric = {
                "values": dict(
                    sorted(
                        nx.closeness_centrality(graph).items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ),
                "description": "Reflects how quickly a node can reach other nodes in the graph",
            }
            metrics["closeness_centrality"] = metric

            # Strongly Connected Components (SCC)
            metric = {
                "values": list(nx.strongly_connected_components(graph)),
                "description": "Lists sets of nodes that are mutually reachable",
            }
            metrics["strongly_connected_components"] = metric

            # Weakly Connected Components (WCC)
            metric = {
                "values": list(nx.weakly_connected_components(graph)),
                "description": "Lists sets of nodes that are connected disregarding edge directions",
            }
            metrics["weakly_connected_components"] = metric

            # Average Path Length (only if the graph is connected)
            if nx.is_strongly_connected(graph):
                metric = {
                    "values": nx.average_shortest_path_length(graph),
                    "description": "Shows the average shortest path length, indicating the graph's efficiency",
                }
                metrics["average_path_length"] = metric

            return metrics

        self.printer.verbose("Attempting to show dependencies")
        if terragrunt_args:
            self.printer.verbose(
                f"- with additional parameters: {' '.join(terragrunt_args)}"
            )

        # Runs the desired command in the directories as defined in the directed graph
        graph = self._get_di_graph(backwards=backwards, working_dir=working_dir)
        try:
            graph.remove_node(r"\n")
        except nx.exception.NetworkXError:
            pass

        # first go through the groups and clean up where needed
        groups = self._prepare_groups(
            graph=graph,
            exclude_external_dependencies=exclude_external_dependencies,
            working_dir=working_dir,
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
        )

        if not groups:
            self.printer.error("No groups in scope, this smells fishy!")
        else:
            self.printer.header("The following groups are in scope:")
            for idx, group in enumerate(groups):
                self.printer.normal(f"\nGroup {idx+1}:")
                for directory in group:
                    self.printer.normal(f"- {directory}")

        if analyze:
            self.printer.header("Graph analysis", print_line_before=True)

            self.printer.bold("Dependencies counts:", print_line_before=True)
            dependencies = calculate_dependencies(graph)
            sorted_dependencies = sorted(
                dependencies.items(), key=lambda x: x[1]["total"], reverse=True
            )
            for node, counts in sorted_dependencies:
                msg = f"""
{node} ->
\ttotal:        {counts['total']}
\tdependent on: {counts['dependent_on_it']}
\tdependencies: {counts['dependencies']}
"""
                self.printer.normal(msg)

            metrics = calculate_graph_metrics(graph)
            for metric, item in metrics.items():
                self.printer.bold(f"Metric: {metric}")
                self.printer.normal(f'Description: {item["description"]}')
                self.printer.normal(
                    json.dumps(item["values"], indent=2, default=set_json_dumps_default)
                )

    def clean(self, working_dir):
        """Remove terragrunt caches and debug files under the working directory."""

        if not working_dir:
            working_dir = os.getcwd()
        for root, dirs, _ in os.walk(working_dir):
            # Remove .terragrunt-cache directories
            for d in dirs:
                if d == ".terragrunt-cache":
                    shutil.rmtree(os.path.join(root, d))

            # Remove terragrunt-debug*.json files
            for pattern in glob.glob(os.path.join(root, "terragrunt-debug*.json")):
                try:
                    os.remove(pattern)
                except OSError as e:
                    self.printer.warning(f"Could not remove {pattern}: {e}")

        self.printer.normal("Cleaned the temporary files")

    def inspect(
        self,
        domain: str,
        substack: str,
        stage: str,
        azure_subscription_id: str,
        config_file: str,
        out: bool,
        data_collection_endpoint: str,
    ):
        """Inspects the status of an Azure deployment"""
        inspector = AzureInspector(
            subscription_id=azure_subscription_id,
            domain=domain,
            substack=substack,
            stage=stage,
            config_file=config_file,
            verbose=self.printer.print_verbose,
        )

        try:
            results = inspector.inspect()

            # Report the status
            exit_code = 0
            self.printer.header("Inspection status:", print_line_before=True)
            for k, v in results.items():
                resource_status = v.get('inspect_status_code', 'NC')
                resource_message = v.get('inspect_message', 'not found')
                msg = (
                    f"{v['type']}: {k}\n"
                    f"        -> Resource:  {resource_status} ({resource_message})"
                )
                if "rbac_assignment_status_code" in v:
                    rbac_status = v['rbac_assignment_status_code']
                    rbac_message = v.get('rbac_assignment_message')
                    msg = (
                        msg
                        + (
                            f"\n        -> RBAC: {rbac_status} ({rbac_message})"
                        )
                    )
                if (
                    v["inspect_status_code"] != "OK"
                    or v.get("rbac_assignment_status_code", "OK") == "NOK"
                ):
                    self.printer.error(msg=msg)
                    exit_code += 1
                else:
                    self.printer.success(msg=msg)

            if out or data_collection_endpoint:
                # convert results to something DCE understands, and add the inputs
                payload = []
                for key, value in results.items():
                    value_with_key = value.copy()
                    value_with_key["resource_type"] = value_with_key.pop("type")
                    value_with_key["resource"] = key
                    value_with_key["domain"] = domain
                    value_with_key["substack"] = substack
                    value_with_key["stage"] = stage
                    value_with_key["subscription_id"] = azure_subscription_id
                    payload.append(value_with_key)

                if out:
                    print(json.dumps(payload, indent=2))

                if data_collection_endpoint:
                    self._post_to_dce(
                        data_collection_endpoint=data_collection_endpoint,
                        payload=payload,
                    )

            return exit_code
        except Exception as e:
            self.printer.normal(f"Exception occurred: {e}")

            if self.printer.print_verbose:
                traceback.print_exc()

            return -1
