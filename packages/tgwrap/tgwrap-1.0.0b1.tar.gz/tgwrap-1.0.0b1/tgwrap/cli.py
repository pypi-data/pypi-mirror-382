#!/usr/bin/env python3

"""This script simply wraps terragrunt (which is a wrapper around terraform...)
and its main function is to allow you to execute a `run-all` command but
broken up in individual steps.

This makes debugging a complex project easier, such as spotting where the
exact problem is.
"""

import os
import sys
from importlib.metadata import PackageNotFoundError, version

import click
import requests
from packaging import version as pkg_version

from .command_constructor import TG_COMMANDS
from .main import STAGES, TgWrap

PACKAGE_NAME = "tgwrap"
try:
    __version__ = version(PACKAGE_NAME)
except PackageNotFoundError:
    __version__ = "0.0.0"


def check_latest_version(verbose=False):
    """Check for later versions on pypi"""

    def echo(msg):
        if not os.getenv("OUTDATED_IGNORE"):
            click.secho(msg, bold=True, file=sys.stderr)

    try:
        # Get latest version from PyPI
        response = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=5)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        # Compare versions using packaging library
        current_ver = pkg_version.parse(__version__)
        latest_ver = pkg_version.parse(latest_version)

        if current_ver < latest_ver:
            echo(
                f"Your local version ({__version__}) is out of date! Latest is {latest_version}!"
            )
        elif verbose:
            echo(f"You are running version {__version__}, latest is {latest_version}")

    except (requests.RequestException, KeyError, pkg_version.InvalidVersion):
        # Handle network errors, missing keys, or invalid version formats
        if verbose:
            echo("Could not determine package version, continue nevertheless.")
        pass
    except Exception:
        # Catch any other unexpected errors
        if verbose:
            echo("Could not determine package version, continue nevertheless.")
        pass


CLICK_CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class DefaultGroup(click.Group):
    """Allow a default command for a group"""

    ignore_unknown_options = True

    def __init__(self, *args, **kwargs):
        default_command = kwargs.pop("default_command", None)
        super().__init__(*args, **kwargs)
        self.default_cmd_name = None
        if default_command is not None:
            self.set_default_command(default_command)

    def set_default_command(self, command):
        """Sets the command that can be omitted (and is considered default)"""
        if isinstance(command, str):
            cmd_name = command
        else:
            cmd_name = command.name
            self.add_command(command)
        self.default_cmd_name = cmd_name

    def parse_args(self, ctx, args):
        if not args and self.default_cmd_name is not None:
            args.insert(0, self.default_cmd_name)
        return super().parse_args(ctx, args)

    def get_command(self, ctx, cmd_name):
        if cmd_name not in self.commands and self.default_cmd_name is not None:
            ctx.args0 = cmd_name
            cmd_name = self.default_cmd_name
        return super().get_command(ctx, cmd_name)

    def resolve_command(self, ctx, args):
        cmd_name, cmd, args = super().resolve_command(ctx, args)
        args0 = getattr(ctx, "args0", None)
        if args0 is not None:
            args.insert(0, args0)
        return cmd_name, cmd, args


@click.group(
    cls=DefaultGroup,
    default_command="run",
    context_settings=CLICK_CONTEXT_SETTINGS,
)
@click.version_option(version=__version__)
def main():
    pass


@main.command(
    name="run",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.argument("command", type=click.Choice(TG_COMMANDS))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    default=False,
    show_default=True,
    help="Run the terragrunt command with debug logging enabled [$TGWRAP_DEBUG]",
    envvar="TGWRAP_DEBUG",
)
@click.option(
    "--no-lock",
    "-n",
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not apply a lock while executing the command [$TGWRAP_NO_LOCK]",
    envvar="TGWRAP_NO_LOCK",
)
@click.option(
    "--update",
    "-u",
    is_flag=True,
    default=False,
    show_default=True,
    help="Delete the contents of the temporary folder to clear out any old, cached source code before downloading new source code into it. [$TG_SOURCE_UPDATE]",
    envvar="TG_SOURCE_UPDATE",
)
@click.option(
    "--upgrade",
    "-U",
    is_flag=True,
    default=False,
    show_default=True,
    help="Installs or upgrade the latest provider versions [$TGWRAP_UPGRADE]",
    envvar="TGWRAP_UPGRADE",
)
@click.option(
    "--planfile",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use the generated planfile when (automatically) applying the changes [$TGWRAP_PLANFILE]",
    envvar="TGWRAP_PLANFILE",
)
@click.option(
    "--planfile-dir",
    "-P",
    default=".terragrunt-cache/current",
    show_default=True,
    help="Relative path to directory with plan file, see README for more details [$TGWRAP_PLANFILE_DIR]",
    envvar="TGWRAP_PLANFILE_DIR",
    type=click.Path(),
)
@click.option(
    "--auto-approve",
    "-a",
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not ask for confirmation before applying planned changes [$TGWRAP_AUTO_APPROVE]",
    envvar="TGWRAP_AUTO_APPROVE",
)
@click.option(
    "--all",
    "-A",
    is_flag=True,
    default=False,
    show_default=True,
    help="Run the specified command on the stack of units in the current directory [$TGWRAP_ALL]",
    envvar="TGWRAP_ALL",
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    default=False,
    show_default=True,
    help="Clean up temporary files such as .terragrunt-cache before executing the command [$TGWRAP_CLEAN]",
    envvar="TGWRAP_CLEAN",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--queue-exclude-external/--queue-include-external",
    "-x/-i",
    is_flag=True,
    default=True,
    show_default=True,
    help="Ignore external dependencies for --all commands [$TG_QUEUE_EXCLUDE_EXTERNAL]",
    envvar="TG_QUEUE_EXCLUDE_EXTERNAL",
)
@click.option(
    "--step-by-step",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Run the graph as triggered by --all step by step and stop when an error occurs [$TGWRAP_STEP_BY_STEP]",
    envvar="TGWRAP_STEP_BY_STEP",
)
@click.option(
    "--continue-on-error",
    "-C",
    is_flag=True,
    default=False,
    show_default=True,
    help="When running in step by step, continue when an error occurs [$TGWRAP_CONTINUE_ON_ERROR]",
    envvar="TGWRAP_CONTINUE_ON_ERROR",
)
@click.option(
    "--start-at-step",
    "-S",
    type=float,
    default=0,
    show_default=True,
    help="When running in step-by-step mode, start processing at the given step number",
)
@click.option(
    "--queue-include-dir",
    "-I",
    multiple=True,
    default=[],
    show_default=True,
    help=r'A glob of a directory that needs to be included, this option can be used multiple times. For example: -I "integrations/\*/\*"',
)
@click.option(
    "--queue-exclude-dir",
    "-E",
    multiple=True,
    default=[],
    show_default=True,
    help=r'A glob of a directory that needs to be excluded, this option can be used multiple times. For example: -E "integrations/\*/\*"',
)
@click.option(
    "--analyze-after-plan",
    is_flag=True,
    default=None,
    show_default=True,
    help="Analyze the results after a plan [$TGWRAP_ANALYZE_AFTER_PLAN]",
    envvar="TGWRAP_ANALYZE_AFTER_PLAN",
)
@click.option(
    "--analyze-config",
    default=None,
    show_default=True,
    help="Name of the analyze config file [$TGWRAP_ANALYZE_CONFIG]",
    envvar="TGWRAP_ANALYZE_CONFIG",
    type=click.Path(),
)
@click.option(
    "--ignore-attributes",
    "-i",
    multiple=True,
    default=[],
    show_default=True,
    help=r"A glob of attributes for which, during plan, updates can be ignored, this option can be used multiple times [$TGWRAP_ANALYZE_IGNORE]",
    envvar="TGWRAP_ANALYZE_IGNORE",
)
@click.option(
    "--data-collection-endpoint",
    "-D",
    default=None,
    show_default=True,
    help="Optional URI of an (Azure) data collection endpoint, to which the analyse results will be sent [$TGWRAP_ANALYZE_DATA_COLLECTION_ENDPOINT]",
    envvar="TGWRAP_ANALYZE_DATA_COLLECTION_ENDPOINT",
)
@click.argument("terragrunt-args", nargs=-1, type=click.UNPROCESSED)
@click.version_option(version=__version__)
def run(
    command: str,
    verbose: bool,
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
    queue_include_dir: list[str],
    queue_exclude_dir: list[str],
    analyze_after_plan: bool,
    analyze_config: bool,
    ignore_attributes: list[str],
    planfile_dir: str,
    data_collection_endpoint: str,
    terragrunt_args: list[str],
):
    """Executes a terragrunt command across multiple projects"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose, check_tg_source=True)
    tgwrap.run(
        command=command,
        debug=debug,
        no_lock=no_lock,
        update=update,
        upgrade=upgrade,
        planfile=planfile,
        planfile_dir=planfile_dir,
        auto_approve=auto_approve,
        all=all,
        clean=clean,
        working_dir=working_dir,
        queue_exclude_external=queue_exclude_external,
        step_by_step=step_by_step,
        continue_on_error=continue_on_error,
        start_at_step=start_at_step,
        include_dirs=queue_include_dir,
        exclude_dirs=queue_exclude_dir,
        analyze_after_plan=analyze_after_plan,
        analyze_config=analyze_config,
        ignore_attributes=ignore_attributes,
        data_collection_endpoint=data_collection_endpoint,
        terragrunt_args=terragrunt_args,
    )


@main.command(
    name="run-all",
    hidden=True,
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
        allow_interspersed_args=False,
    ),
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run_all_deprecated(*args, **kwargs):
    """This command is deprecated, please use 'run' with the --all option"""
    click.secho(
        "The 'run-all' command is deprecated, please use 'run' with the --all option",
        fg="yellow",
        bold=True,
        file=sys.stderr,
    )
    sys.exit(1)


@main.command(
    name="analyze",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.option(
    "--queue-exclude-external/--queue-include-external",
    "-x/-i",
    is_flag=True,
    default=True,
    show_default=True,
    help="Ignore external dependencies for --all commands [$TG_QUEUE_EXCLUDE_EXTERNAL]",
    envvar="TG_QUEUE_EXCLUDE_EXTERNAL",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--start-at-step",
    "-S",
    type=float,
    default=0,
    show_default=True,
    help="When running in step-by-step mode, start processing at the given step number",
)
@click.option(
    "--out",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show output as json %[$TGWRAP_OUTPUT_AS_JSON]",
    envvar="TGWRAP_OUTPUT_AS_JSON",
)
@click.option(
    "--analyze-config",
    default=None,
    show_default=True,
    help="Name of the analyze config file (or set TGWRAP_ANALYZE_CONFIG environment variable)",
    envvar="TGWRAP_ANALYZE_CONFIG",
    type=click.Path(),
)
@click.option(
    "--ignore-attributes",
    "-i",
    multiple=True,
    default=[],
    show_default=True,
    help=r"A glob of attributes for which updates can be ignored, this option can be used multiple times (or set TGWRAP_ANALYZE_IGNORE environment variable)",
    envvar="TGWRAP_ANALYZE_IGNORE",
)
@click.option(
    "--queue-include-dir",
    "-I",
    multiple=True,
    default=[],
    show_default=True,
    help=r'A glob of a directory that needs to be included, this option can be used multiple times. For example: -I "integrations/\*/\*"',
)
@click.option(
    "--queue-exclude-dir",
    "-E",
    multiple=True,
    default=[],
    show_default=True,
    help=r'A glob of a directory that needs to be excluded, this option can be used multiple times. For example: -E "integrations/\*/\*"',
)
@click.option(
    "--planfile-dir",
    "-P",
    default=None,
    show_default=True,
    help="Relative path to directory with plan file (or set TGWRAP_PLANFILE_DIR environment variable), see README for more details",
    envvar="TGWRAP_PLANFILE_DIR",
    type=click.Path(),
)
@click.option(
    "--data-collection-endpoint",
    "-D",
    default=None,
    show_default=True,
    help="Optional URI of an (Azure) data collection endpoint, to which the analyse results will be sent",
    envvar="TGWRAP_ANALYZE_DATA_COLLECTION_ENDPOINT",
)
@click.argument("terragrunt-args", nargs=-1, type=click.UNPROCESSED)
@click.version_option(version=__version__)
def run_analyze(
    verbose,
    queue_exclude_external,
    working_dir,
    start_at_step,
    out,
    analyze_config,
    ignore_attributes,
    queue_include_dir,
    queue_exclude_dir,
    planfile_dir,
    data_collection_endpoint,
    terragrunt_args,
):
    """Analyzes the plan files"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose, check_tg_source=(planfile_dir is None))
    tgwrap.analyze(
        queue_exclude_external=queue_exclude_external,
        working_dir=working_dir,
        start_at_step=start_at_step,
        out=out,
        analyze_config=analyze_config,
        ignore_attributes=ignore_attributes,
        include_dirs=queue_include_dir,
        exclude_dirs=queue_exclude_dir,
        planfile_dir=planfile_dir,
        data_collection_endpoint=data_collection_endpoint,
        terragrunt_args=terragrunt_args,
    )


@main.command(
    name="sync",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--source-domain",
    "-S",
    default="",
    show_default=True,
    help="Source domain of config files, when omitted the DLZ where you run this command is assumed.",
)
@click.option(
    "--target-domain",
    "-T",
    default="",
    show_default=True,
    help="Target domain where config files will be copied to, when omitted the DLZ where you run this command is assumed.",
)
@click.option(
    "--source-stage",
    "-s",
    required=True,
    type=click.Choice(STAGES, case_sensitive=True),
    help="Source stage of config files",
)
@click.option(
    "--target-stage",
    "-t",
    type=click.Choice(STAGES, case_sensitive=True),
    help="Target of config files",
)
@click.option(
    "--module",
    "-m",
    default="",
    show_default=True,
    help="Name of the module, if omitted all modules will be copied.",
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    default=False,
    show_default=True,
    help="Clean up files on target side that do not exist as source [$TGWRAP_CLEAN]",
    envvar="TGWRAP_CLEAN",
)
@click.option(
    "--include-dotenv-file",
    "-i",
    is_flag=True,
    default=False,
    show_default=True,
    help="Include the .env (or .envrc) files [$TGWRAP_INCLUDE_DOTENV_FILE]",
    envvar="TGWRAP_INCLUDE_DOTENV_FILE",
)
@click.option(
    "--auto-approve",
    "-a",
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not ask for confirmation before applying planned changes [$TGWRAP_AUTO_APPROVE]",
    envvar="TGWRAP_AUTO_APPROVE",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.version_option(version=__version__)
def sync(
    source_domain,
    source_stage,
    target_domain,
    target_stage,
    module,
    auto_approve,
    clean,
    include_dotenv_file,
    working_dir,
    verbose,
):
    """Syncs the terragrunt units from one stage to another (and possibly to a different domain)"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose)
    tgwrap.sync(
        source_domain=source_domain,
        source_stage=source_stage,
        target_domain=target_domain,
        target_stage=target_stage,
        module=module,
        auto_approve=auto_approve,
        clean=clean,
        include_dotenv_file=include_dotenv_file,
        working_dir=working_dir,
    )


@main.command(
    name="sync-dir",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--source-directory",
    "-s",
    required=True,
    help="Directory where source config files reside.",
)
@click.option(
    "--target-directory",
    "-t",
    required=True,
    help="Directory where config files will be synced to.",
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    default=False,
    show_default=True,
    help="Clean up files on target side that do not exist as source [$TGWRAP_CLEAN]",
    envvar="TGWRAP_CLEAN",
)
@click.option(
    "--include-dotenv-file",
    "-i",
    is_flag=True,
    default=False,
    show_default=True,
    help="Include the .env (or .envrc) files [$TGWRAP_INCLUDE_DOTENV_FILE]",
    envvar="TGWRAP_INCLUDE_DOTENV_FILE",
)
@click.option(
    "--auto-approve",
    "-a",
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not ask for confirmation before applying planned changes [$TGWRAP_AUTO_APPROVE]",
    envvar="TGWRAP_AUTO_APPROVE",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.version_option(version=__version__)
def sync_dir(
    source_directory,
    target_directory,
    auto_approve,
    clean,
    include_dotenv_file,
    working_dir,
    verbose,
):
    """Syncs the terragrunt units from one directory to anothery"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose)
    tgwrap.sync_dir(
        source_directory=source_directory,
        target_directory=target_directory,
        auto_approve=auto_approve,
        clean=clean,
        include_dotenv_file=include_dotenv_file,
        working_dir=working_dir,
    )


@main.command(
    name="deploy",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--manifest-file",
    "-m",
    help="Manifest file describing the deployment options",
    required=True,
    default="manifest.yaml",
    show_default=True,
    type=click.Path(),
)
@click.option(
    "--version-tag",
    "-V",
    required=False,
    default=None,
    show_default=True,
    help="Version tag, use 'latest' to, well, get the latest version [$TGWRAP_DEPLOY_VERSION_TAG]",
    envvar="TGWRAP_DEPLOY_VERSION_TAG",
)
@click.option(
    "--target-stage",
    "-t",
    multiple=True,
    required=True,
    help="Stage to deploy to",
    type=click.Choice(STAGES, case_sensitive=True),
)
@click.option(
    "--include-global-config-files/--exclude-global-config-files",
    "-i/-x",
    is_flag=True,
    default=True,
    show_default=True,
    help="Whether or not to include deploying the (in the manifest specified) global config files [$TGWRAP_DEPLOY_INCLUDE_GLOBAL_CONFIG_FILES]",
    envvar="TGWRAP_DEPLOY_INCLUDE_GLOBAL_CONFIG_FILES",
)
@click.option(
    "--auto-approve",
    "-a",
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not ask for confirmation before applying planned changes [$TGWRAP_AUTO_APPROVE]",
    envvar="TGWRAP_AUTO_APPROVE",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.version_option(version=__version__)
def deploy(
    manifest_file,
    version_tag,
    target_stage,
    include_global_config_files,
    auto_approve,
    working_dir,
    verbose,
):
    """Deploys the terragrunt units from a git repository"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose)
    tgwrap.deploy(
        manifest_file=manifest_file,
        version_tag=version_tag,
        target_stages=target_stage,
        include_global_config_files=include_global_config_files,
        auto_approve=auto_approve,
        working_dir=working_dir,
    )


@main.command(
    name="check-deployments",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--platform-repo-url",
    "-p",
    required=True,
    help="URL of the platform git repository [$TGWRAP_PLATFORM_REPO_URL]",
    envvar="TGWRAP_PLATFORM_REPO_URL",
)
@click.option(
    "--levels-deep",
    "-l",
    required=True,
    default=5,
    show_default=True,
    help="For how many (directory) levels deep must be searched for deployments [$TGWRAP_CHECK_LEVELS_DEEP]",
    envvar="TGWRAP_CHECK_LEVELS_DEEP",
    type=int,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose printing",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--out",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show output as json %[$TGWRAP_OUTPUT_AS_JSON]",
    envvar="TGWRAP_OUTPUT_AS_JSON",
)
@click.version_option(version=__version__)
def check_deployments(platform_repo_url, levels_deep, verbose, working_dir, out):
    """Check the freshness of deployed configuration versions against the platform repository"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose)
    tgwrap.check_deployments(
        repo_url=platform_repo_url,
        levels_deep=levels_deep,
        working_dir=working_dir,
        out=out,
    )


@main.command(
    name="show-graph",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--backwards",
    "-b",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether or not the graph must be shown backwards",
)
@click.option(
    "--exclude-external-dependencies/--include-external-dependencies",
    "-x/-i",
    is_flag=True,
    default=True,
    show_default=True,
    help="Whether or not external dependencies must be ignored",
)
@click.option(
    "--analyze",
    "-a",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show analysis of the graph",
)
@click.option(
    "--queue-include-dir",
    "-I",
    multiple=True,
    default=[],
    show_default=True,
    help=r'A glob of a directory that needs to be included, this option can be used multiple times. For example: -I "integrations/\*/\*"',
)
@click.option(
    "--queue-exclude-dir",
    "-E",
    multiple=True,
    default=[],
    show_default=True,
    help=r'A glob of a directory that needs to be excluded, this option can be used multiple times. For example: -E "integrations/\*/\*"',
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.argument("terragrunt-args", nargs=-1, type=click.UNPROCESSED)
@click.version_option(version=__version__)
def show_graph(
    backwards,
    exclude_external_dependencies,
    analyze,
    working_dir,
    queue_include_dir,
    queue_exclude_dir,
    verbose,
    terragrunt_args,
):
    """Shows the dependencies of a project"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose, check_tg_source=True)
    tgwrap.show_graph(
        backwards=backwards,
        exclude_external_dependencies=exclude_external_dependencies,
        analyze=analyze,
        working_dir=working_dir,
        include_dirs=queue_include_dir,
        exclude_dirs=queue_exclude_dir,
        terragrunt_args=terragrunt_args,
    )


@main.command(
    name="clean",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose printing",
)
@click.option(
    "--working-dir",
    "-w",
    default=None,
    show_default=True,
    help="Working directory, when omitted the current directory is used [$TGWRAP_WORKING_DIR]",
    envvar="TGWRAP_WORKING_DIR",
)
@click.version_option(version=__version__)
def clean(verbose, working_dir):
    """Clean the temporary files of a terragrunt/terraform project"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose)
    tgwrap.clean(
        working_dir=working_dir,
    )


@main.command(
    name="inspect",
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "--domain",
    "-d",
    required=True,
    help="Domain name used in naming the objects [$TGWRAP_INSPECT_DOMAIN]",
    envvar="TGWRAP_INSPECT_DOMAIN",
)
@click.option(
    "--substack",
    "-S",
    default=None,
    show_default=True,
    help="Identifier that is needed to select the objects [$TGWRAP_INSPECT_SUBSTACK]",
    envvar="TGWRAP_INSPECT_SUBSTACK",
)
@click.option(
    "--stage",
    "-s",
    required=True,
    help="Stage (environment) to verify [$TGWRAP_INSPECT_STAGE]",
    envvar="TGWRAP_INSPECT_STAGE",
)
@click.option(
    "--azure-subscription-id",
    "-a",
    required=True,
    help="Azure subscription id where the objects reside [$TGWRAP_INSPECT_AZURE_SUBSCRIPTION_ID]",
    envvar="TGWRAP_INSPECT_AZURE_SUBSCRIPTION_ID",
)
@click.option(
    "--config-file",
    "-c",
    required=True,
    type=click.Path(),
    help="Config file specifying the verifications to be performed [$TGWRAP_INSPECT_CONFIG_FILE]",
    envvar="TGWRAP_INSPECT_CONFIG_FILE",
)
@click.option(
    "--out",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show output as json %[$TGWRAP_OUTPUT_AS_JSON]",
    envvar="TGWRAP_OUTPUT_AS_JSON",
)
@click.option(
    "--data-collection-endpoint",
    "-D",
    default=None,
    show_default=True,
    help="Optional URI of an (Azure) data collection endpoint, to which the inspection results will be sent",
    envvar="TGWRAP_INSPECT_DATA_COLLECTION_ENDPOINT",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verbose output [$TGWRAP_VERBOSE]",
    envvar="TGWRAP_VERBOSE",
)
@click.version_option(version=__version__)
def inspect(
    domain,
    substack,
    stage,
    azure_subscription_id,
    config_file,
    out,
    data_collection_endpoint,
    verbose,
):
    """Inspect the status of an (Azure) environment"""
    check_latest_version(verbose)

    tgwrap = TgWrap(verbose=verbose)
    exit = tgwrap.inspect(
        domain=domain,
        substack=substack,
        stage=stage,
        azure_subscription_id=azure_subscription_id,
        out=out,
        data_collection_endpoint=data_collection_endpoint,
        config_file=config_file,
    )

    sys.exit(exit)


# this is needed for the vscode debugger to work
if __name__ == "__main__":
    main()
