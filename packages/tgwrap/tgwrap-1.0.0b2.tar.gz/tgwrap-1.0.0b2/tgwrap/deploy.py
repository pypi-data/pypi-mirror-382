"""A set of utility functions related to deploying projects"""

import os
import re
import shlex
import shutil
import subprocess
import sys

from .printer import Printer


def run_sync(
    source_path,
    target_path,
    auto_approve,
    include_dotenv_file,
    clean,
    terragrunt_file,
    excludes=None,
    source_stage=None,
    target_stage=None,
    source_domain=None,
    verbose=False,
):
    """Run a sync copying files from a source to a target path"""

    def is_installed(program):
        """Checks if a program is installed on the system"""
        return shutil.which(program) is not None

    printer = Printer(verbose)

    if not is_installed("rsync"):
        printer.error("'rsync' seems not installed. Cannot continue")
    elif not os.path.exists(source_path):
        printer.error(f"Cannot find {source_path}. Cannot continue.")
        if source_domain:
            printer.error(
                "Please ensure you are in the directory that contains your projects, "
                + "or use --working-dir option"
            )
        else:
            printer.error(
                "Please ensure you are in the root of your project, or use --working-dir option"
            )
    else:
        printer.verbose(f"Copying config: {source_path} => {target_path}")

        try:
            os.makedirs(target_path)
        except OSError:
            # directory already exists
            pass

        clean_stmt = "--delete" if clean else ""
        env_file_stmt = (
            "--exclude='env.hcl'"
            if source_stage != target_stage
            else "--include='env.hcl'"
        )
        dotenv_file_stmt = (
            "--include='.env' --include='.envrc'"
            if include_dotenv_file
            else "--exclude='.env' --exclude='.envrc'"
        )
        excludes_stmt = (
            " ".join([f"--exclude={x}" for x in excludes]) if excludes else ""
        )

        include_statements = ""
        #
        # Note: this logic is somewhat flawed, basically if the target doesn't exist it assumes it must be
        # a directory, which is not always what you want!!!!!
        #
        if os.path.isdir(target_path):
            include_statements = (
                f"--include='{terragrunt_file}' {dotenv_file_stmt} {env_file_stmt} {excludes_stmt} "
                + "--exclude='.terragrunt-cache/' --exclude='.terraform/' "
                + "--exclude='terragrunt-debug.tfvars.json' --exclude=planfile "
                + "--exclude='.DS_Store' --exclude='*.log' "
            )

        cmd = (
            f"rsync -aim {clean_stmt} "
            + include_statements
            + f"{source_path} {target_path}"
        )

        cmd = re.sub(" +", " ", cmd)

        printer.header("Will be deploying:", print_line_before=True)
        printer.normal(f"from: {source_path}")
        printer.normal(f"to:   {target_path}")
        printer.verbose(f"Using command:\n$ {cmd}")

        if not auto_approve:
            response = input("\nDo you want to continue? (y/N) ")
            if response.lower() != "y":
                sys.exit(1)

        rc = subprocess.run(shlex.split(cmd), check=True)
        printer.verbose(rc)


def prepare_deploy_config(
    step,
    config,
    source_dir,
    source_config_dir,
    target_dir,
    target_stage,
    substacks,
    substack_configs,
    tg_file_name,
    verbose=False,
):
    """Prepare the deploy configuration for a partiuclar stage"""

    def get_directories(source_path):
        directories = []
        for root, subdirs, _ in os.walk(source_path):
            for dir in subdirs:
                directory_path = os.path.join(root, dir)
                directories.append(os.path.basename(directory_path))
        return directories

    printer = Printer(verbose)
    deploy_actions = {}

    source_stage = config["source_stage"]
    printer.verbose(f"Found deployment step {step} using source stage {source_stage}")

    source_path = os.path.join(source_dir, source_stage, config.get("source_dir", ""))
    source_modules = {
        entry: {}
        for entry in os.listdir(source_path)
        if os.path.isdir(os.path.join(source_path, entry))
    }
    printer.verbose(f"Found modules: {source_modules}")

    # check if we want to deploy modules
    if config.get("skip_all_modules", False):
        include_modules = {}
    else:
        include_modules = (
            config.get("include_modules")
            if len(config.get("include_modules", [])) > 0
            else source_modules
        )

    printer.verbose(f"Include modules: {include_modules}")

    # optionally, the moduels can be placed in another dir than the current
    base_dir = config.get("base_dir", "")

    for module, module_details in include_modules.items():
        source_module = module_details.get("source", module)
        target_module = module_details.get("target", module)

        full_source_path = os.path.join(source_path, source_module, "")
        full_target_path = os.path.join(target_dir, base_dir, target_module, "")

        if not os.path.exists(full_source_path):
            printer.error(
                f"Path {full_source_path} does not exist, this seems a config error!"
            )
        elif not os.path.isfile(os.path.join(full_source_path, tg_file_name)):
            printer.warning(
                f"Module {source_module} seems substack and not a terragrunt module: skip it!"
            )
        elif (
            source_module in config.get("exclude_modules", [])
            or source_module in substacks
        ):
            printer.verbose(f"Exclude module {source_module}")
        else:
            key = f"base -> {os.path.join(base_dir, module)}" if base_dir else module
            deploy_actions[key] = {
                "source": full_source_path,
                "target": full_target_path,
            }
    config_dir = config.get("config_dir", None)
    module_name = os.path.basename(os.getcwd())

    if len(config.get("configs", [])) > 0:
        # run some checks and sets some variables
        if not source_config_dir:
            raise Exception(
                "Config files must be deployed but 'config_path' variable is not set!"
            )
        if not config_dir:
            raise Exception(
                "Config files must be deployed but 'config_dir' variable is not set!"
            )

        target_path = os.path.join(
            target_dir,
            config_dir,
            module_name,
            target_stage,
            "",
        )
        # the target path might not exist
        try:
            os.makedirs(target_path)
        except FileExistsError:
            pass

    for cfg in config.get("configs", []):
        printer.verbose(f"Found config file : {cfg}")

        source_path = os.path.join(source_config_dir, source_stage, cfg)

        full_target_path = os.path.dirname(os.path.join(target_path, cfg))
        if os.path.exists(source_path):
            deploy_actions[f"configs -> {cfg}"] = {
                "source": source_path,
                "target": full_target_path,
            }
        else:
            printer.warning(f"Source path of config file does not exist: {source_path}")

    for ss, substack in substack_configs:
        if (
            "applies_to_stages" in substack
            and target_stage not in substack["applies_to_stages"]
        ):
            printer.verbose(
                f"Target stage {target_stage} not applicable for substack {ss}."
            )
        else:
            printer.verbose(f"Found substack : {ss}")

            source_path = os.path.join(source_dir, source_stage, substack["source"], "")
            source_modules = {
                entry: {}
                for entry in os.listdir(source_path)
                if os.path.isdir(os.path.join(source_path, entry))
            }
            target_path = os.path.join(target_dir, substack["target"], "")

            printer.verbose(f"Include substack modules: {include_modules}")

            include_modules = substack.get("include_modules", [])

            if include_modules:
                # get all directories in the substack and create an exlude_modules list from that
                source_directories = get_directories(source_path)
                exclude_modules = list(set(source_directories) - set(include_modules))
            else:
                exclude_modules = substack.get("exclude_modules", [])

            printer.verbose(f"Include modules: {include_modules}")
            printer.verbose(f"Exclude modules: {include_modules}")

            if os.path.exists(source_path):
                deploy_actions[f'substack -> {substack["target"]}'] = {
                    "source": source_path,
                    "target": target_path,
                    "excludes": exclude_modules,
                }
            else:
                printer.warning(
                    f"Source path of substack does not exist: {source_path}"
                )

            if len(substack.get("configs", [])) > 0:
                # run some checks and sets some variables
                if not source_config_dir:
                    raise Exception(
                        "Config files must be deployed but 'config_path' variable is not set!"
                    )
                if not config_dir:
                    raise Exception(
                        "Config files must be deployed but 'config_dir' variable is not set!"
                    )

                target_path = os.path.join(
                    target_dir,
                    config_dir,
                    module_name,
                    target_stage,
                    substack["target"],
                    "",
                )
                # the target path might not exist
                try:
                    os.makedirs(target_path)
                except FileExistsError:
                    pass

            for cfg in substack.get("configs", []):
                printer.verbose(f"Found substack config file : {cfg}")

                full_source_path = os.path.join(
                    source_config_dir, source_stage, substack["source"], cfg
                )

                full_target_path = os.path.dirname(os.path.join(target_path, cfg))
                # print("source: ", full_source_path)
                # print("target: ", full_target_path)
                if os.path.exists(source_path):
                    deploy_actions[
                        f"substack {substack['target']} configs -> {os.path.join(substack['source'], cfg)}"
                    ] = {
                        "source": full_source_path,
                        "target": full_target_path,
                    }
                else:
                    printer.warning(
                        f"Source path of config file does not exist: {source_path}"
                    )

    return deploy_actions
