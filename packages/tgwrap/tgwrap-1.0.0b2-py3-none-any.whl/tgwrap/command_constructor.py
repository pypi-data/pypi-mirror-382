"""Command constructor for building terragrunt commands in an elegant and maintainable way.
"""

import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

from .printer import Printer

TG_RO_COMMANDS = [
    "console",
    "fmt",
    "graph",
    "init",
    "import",
    "login",
    "logout",
    "metadata",
    "output",
    "plan",
    "providers",
    "show",
    "test",
    "version",
    "validate",
    "workspace",
    "force-unlock",
    "state",
]

TG_RW_COMMANDS = [
    "get",
    "apply",
    "destroy",
    "import" "refresh",
    "taint",
    "untaint",
]

TG_COMMANDS = TG_RO_COMMANDS + TG_RW_COMMANDS


@dataclass
class CommandConfig:
    """Configuration for terragrunt command construction"""

    command: str
    debug: bool = False
    exclude_external_dependencies: bool = False
    all: bool = False
    step_by_step: bool = False
    non_interactive: bool = True
    no_auto_approve: bool = True
    no_lock: bool = True
    update: bool = False
    upgrade: bool = False
    planfile: bool = True
    working_dir: Optional[str] = None
    include_dirs: Optional[list[str]] = None
    exclude_dirs: Optional[list[str]] = None
    terragrunt_args: Optional[list[str]] = None

    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.include_dirs is None:
            self.include_dirs = []
        if self.exclude_dirs is None:
            self.exclude_dirs = []
        # Normalize command to lowercase
        self.command = self.command.lower()


@dataclass
class CommandComponents:
    """Components that make up the final command"""

    base_command: str = ""
    lock_stmt: str = ""
    all_stmt: str = ""
    interactive_stmt: str = ""
    update_stmt: str = ""
    ignore_deps_stmt: str = ""
    debug_stmt: str = ""
    working_dir_stmt: str = ""
    upgrade_stmt: str = ""
    planfile_stmt: str = ""
    auto_approve_stmt: str = ""
    include_dir_stmt: str = ""
    exclude_dir_stmt: str = ""
    tg_args_statement: str = ""


class TgCommandConstructor:
    """Constructs terragrunt commands in a clean, maintainable way.

    This class encapsulates the logic for building terragrunt commands with various
    options and configurations, making it easier to test and maintain than a single
    large method.
    """

    PLANFILE_NAME = "planfile"
    TG_FILE = "terragrunt.hcl"
    TG_SOURCE_VAR = "TG_SOURCE"
    TG_SOURCE_MAP_VAR = "TG_SOURCE_MAP"
    MINIMUM_TG_VERSION = "0.88.0"

    # Command templates for different scenarios
    COMMAND_TEMPLATES = {
        "run_all_base": "terragrunt run {all} {update} {interactive} {debug} {working_dir} {include_dirs} {exclude_dirs} {command}",
        "run_single_base": "terragrunt run -- {command}",
        "terraform_args": "-- {auto_approve} {upgrade} {planfile} {lock}",
        "clean": "clean",  # Special case
    }

    def __init__(
        self, printer: Printer, check_tg_source: bool, skip_version_check: bool = False
    ):
        """Initialize the command constructor.

        Args:
            printer: Printer instance for logging
            check_tg_source: Whether to check and configure TG_SOURCE variables
            skip_version_check: Whether to skip terragrunt version check (useful for testing)
        """
        self.printer = printer

        self.tg_source_indicator = None
        if check_tg_source:
            # Check if the "TG_SOURCE" or "TG_SOURCE_MAP" environment variable is set
            # TG_SOURCE takes precedence
            if self.TG_SOURCE_MAP_VAR in os.environ:
                self.printer.warning(
                    f"'{self.TG_SOURCE_MAP_VAR}' environment variable is set with addresses: '{os.environ[self.TG_SOURCE_MAP_VAR]}'!"
                )
                self.tg_source_indicator = self.TG_SOURCE_MAP_VAR

                # if also TG_SOURCE_VAR is set, delete it to avoid it overriding the source map
                if self.TG_SOURCE_VAR in os.environ:
                    del os.environ[self.TG_SOURCE_VAR]
            elif self.TG_SOURCE_VAR in os.environ:
                self.printer.warning(
                    f"'{self.TG_SOURCE_VAR}' environment variable is set with address: '{os.environ[self.TG_SOURCE_VAR]}'!"
                )
                self.tg_source_indicator = self.TG_SOURCE_VAR
            else:
                self.printer.success(
                    "No 'TG_SOURCE[_MAP]' variable is set, so the sources as defined in terragrunt.hcl files will be used as is!"
                )
                self.tg_source_indicator = None

        # Check terragrunt version on initialization (unless skipped for testing)
        if not skip_version_check:
            self._check_terragrunt_version()

    def _parse_version(self, version_string: str) -> tuple[int, int, int]:
        """Parse version string and return tuple of integers (major, minor, patch).

        Args:
            version_string: Version string like "0.88.0" or "v0.88.0"

        Returns:
            Tuple of (major, minor, patch) as integers

        Raises:
            ValueError: If version string cannot be parsed
        """
        # Remove 'v' prefix if present
        clean_version = version_string.lstrip("v")

        # Split version into parts
        try:
            parts = clean_version.split(".")
            if len(parts) != 3:
                raise ValueError(f"Version must have exactly 3 parts: {version_string}")

            major, minor, patch = map(int, parts)
            return (major, minor, patch)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid version format '{version_string}': {e}")

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        v1_parts = self._parse_version(version1)
        v2_parts = self._parse_version(version2)

        if v1_parts < v2_parts:
            return -1
        if v1_parts > v2_parts:
            return 1

        return 0

    def _get_terragrunt_version(self) -> Optional[str]:
        """Get the current terragrunt version.

        Returns:
            Version string if successful, None if terragrunt not found or version cannot be determined
        """
        try:
            return self._get_version()
        except Exception as e:
            self.printer.warning(f"Error checking terragrunt version: {e}")
            return None

    def _get_version(self) -> Optional[str]:
        """Original version detection method"""
        result = subprocess.run(
            ["terragrunt", "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            version_match = re.search(r"v?(\d+\.\d+\.\d+)", output)
            if version_match:
                return version_match.group(1)

            self.printer.warning(
                f"Could not parse version from terragrunt output: {output}"
            )
            return None
        else:
            self.printer.error(
                f"Terragrunt version command failed with return code {result.returncode}"
            )
            self.printer.error(f"Error output: {result.stderr}")
            return None

    def _check_terragrunt_version(self) -> bool:
        """Check if the installed terragrunt version meets the minimum requirement.

        Returns:
            True if version is sufficient, False otherwise
        """
        current_version = self._get_terragrunt_version()
        if current_version is None:
            self.printer.error(
                f"Could not determine terragrunt version. Minimum required: v{self.MINIMUM_TG_VERSION}"
            )
            return False

        try:
            comparison = self._compare_versions(
                current_version, self.MINIMUM_TG_VERSION
            )

            if comparison >= 0:
                self.printer.verbose(
                    f"Terragrunt version v{current_version} meets minimum requirement v{self.MINIMUM_TG_VERSION}"
                )
                return True

            self.printer.error(
                f"Terragrunt version v{current_version} is below minimum required version v{self.MINIMUM_TG_VERSION}. "
                f"Please upgrade terragrunt to continue."
            )
            sys.exit(1)

        except ValueError as e:
            self.printer.error(f"Error comparing terragrunt versions: {e}")
            return False

    def construct_command(
        self,
        command: str,
        debug: bool,
        queue_exclude_external: bool,
        all: bool = False,
        step_by_step: bool = False,
        non_interactive: bool = True,
        no_auto_approve: bool = True,
        no_lock: bool = True,
        update: bool = False,
        upgrade: bool = False,
        planfile: bool = True,
        working_dir: Optional[str] = None,
        include_dirs: Optional[list[str]] = None,
        exclude_dirs: Optional[list[str]] = None,
        terragrunt_args: Optional[list[str]] = None,
    ) -> str:
        """Constructs a terragrunt command with the specified options.

        Args:
            command: The terragrunt command to execute
            debug: Enable debug mode
            queue_exclude_external: Ignore external dependencies for --all commands.
            all: Use --all flag for run-all mode
            step_by_step: run multiple modules in step-by-step mode
            non_interactive: Run in non-interactive mode
            no_auto_approve: Disable auto-approval for destructive operations
            no_lock: Disable state locking
            update: Update sources
            upgrade: Upgrade providers
            planfile: Use planfile for apply/destroy operations
            working_dir: Working directory for the command
            include_dirs: Directories to include
            exclude_dirs: Directories to exclude
            terragrunt_args: Additional terragrunt arguments

        Returns:
            The complete terragrunt command string
        """

        config = CommandConfig(
            command=command,
            debug=debug,
            exclude_external_dependencies=queue_exclude_external,
            all=all,
            step_by_step=step_by_step,
            non_interactive=non_interactive,
            no_auto_approve=no_auto_approve,
            no_lock=no_lock,
            update=update,
            upgrade=upgrade,
            planfile=planfile,
            working_dir=working_dir,
            include_dirs=include_dirs or [],
            exclude_dirs=exclude_dirs or [],
            terragrunt_args=terragrunt_args,
        )

        components = self._build_command_components(config)
        return self._assemble_final_command(config, components)

    def _complete_tg_source(
        self, all: bool, step_by_step: bool, working_dir: Optional[str]
    ) -> bool:
        """Complete the TG_SOURCE variable if needed.

        When using 'run --all', TG_SOURCE can point to the root of the repo.
        However, when using 'run' (single mode), TG_SOURCE must point to the
        specific module, otherwise terragrunt will fail.

        So in that case we try to parse the source from the terragrunt.hcl file
        and update TG_SOURCE accordingly. If that is not possible, we will
        fall back to using 'run -all' (if allowed).

        Args:
            all: Whether to use run-all mode
            working_dir: Working directory for the command

        Returns:
            True if should use run-all mode, False for single run mode
        """

        def extract_source_value(terragrunt_file_content):
            """Extract source value from terragrunt.hcl content"""
            # Regular expression to capture the terraform block
            terraform_block_pattern = re.compile(r"terraform\s*\{(.*?)\n\}", re.DOTALL)

            # Regular expression to capture the 'source' key and its value
            source_pattern = re.compile(r'source\s*=\s*"(.*?)(?<!\\)"', re.DOTALL)

            # Find the terraform block
            terraform_block_match = terraform_block_pattern.search(
                terragrunt_file_content
            )
            if terraform_block_match:
                terraform_block = terraform_block_match.group(1)

                # Search for the 'source' key within the block
                source_match = source_pattern.search(terraform_block)
                if source_match:
                    return source_match.group(1)  # Return the value of 'source'

                return None
            else:
                raise ValueError("Could not locate the terragrunt source value")

        # If we are running 'run-all' mode, we use run-all
        if all or step_by_step:
            use_run_all = True
        else:
            # Default to single run mode for single module execution
            use_run_all = False
            source_module = None

            # Only try TG_SOURCE optimization if we have a tg_source_indicator
            if self.tg_source_indicator:
                # So we are in single mode and there should be a terragrunt.hcl file in this directory.
                # Check if we can get the module part from the source definition in this file.
                tg_file = self.TG_FILE
                if working_dir:
                    tg_file = os.path.join(working_dir, tg_file)

                try:
                    with open(tg_file) as file:
                        content = file.read()
                        source = extract_source_value(content)

                        source_module = None
                        if source:
                            # get the source part, typically the last part after the double /.
                            # also remove a potential version element from it.
                            source_module = re.sub(
                                r"\${[^}]*}", "", source.split("//")[::-1][0]
                            )
                            self.printer.verbose(
                                f"Extracted source module from {self.TG_FILE}: {source_module}"
                            )
                except Exception as e:
                    self.printer.warning(
                        "Could not parse terragrunt.hcl, but we fall back to default behaviour."
                    )
                    self.printer.verbose(f"error (of type {type(e)}) raised")

                # if we were able to determine source_module, we can assign it to TG_SOURCE
                if source_module:
                    # we can update the terragrunt source map to fully refer to the module, and then no need for a run --all
                    if self.tg_source_indicator == self.TG_SOURCE_MAP_VAR:
                        self.printer.verbose(
                            f"{self.TG_SOURCE_MAP_VAR} environment variable is set, updating this is not supported (yet)."
                        )
                        # so we use run --all in this case, which can work with the root of the repo set as source
                        use_run_all = True
                    elif self.tg_source_indicator == self.TG_SOURCE_VAR:
                        tg_source = f'{os.environ.get(self.TG_SOURCE_VAR, '').rstrip("//.")}//{source_module}'
                        os.environ[self.TG_SOURCE_VAR] = tg_source
                        self.printer.verbose(
                            f"{self.TG_SOURCE_VAR} environment variable manipulated for extra performance (no --all): {tg_source}"
                        )
                    else:
                        self.printer.verbose(
                            "Performance enhancements allowed but was not able to configure it."
                        )

                else:
                    # We have a source indicator but were not able to construct a full path to the module
                    # Hence we need to fall back on the run --all mode as in that case terragrunt will
                    # adjust for it
                    use_run_all = True

        return use_run_all

    def _build_command_components(self, config: CommandConfig) -> CommandComponents:
        """Build all command components"""
        components = CommandComponents()

        components.lock_stmt = self._build_lock_statement(config)
        components.debug_stmt = self._build_debug_statement(config)

        use_run_all = self._complete_tg_source(
            all=config.all,
            step_by_step=config.step_by_step,
            working_dir=config.working_dir,
        )

        self._build_run_components(config, components)
        if use_run_all:
            self._build_run_all_components(config, components)

        components.upgrade_stmt = "-upgrade" if config.upgrade and config.command in ['init'] else ""
        components.planfile_stmt = self._build_planfile_statement(config)
        # Use shlex.quote to properly escape each argument
        components.tg_args_statement = (
            " ".join(shlex.quote(arg) for arg in config.terragrunt_args) if config.terragrunt_args else ""
        )

        return components

    def _build_lock_statement(self, config: CommandConfig) -> str:
        """Build the lock statement"""
        potential_unlocked_commands = ["init", "plan", "output"]

        if config.no_lock and config.command in potential_unlocked_commands:
            self.printer.warning("State will NOT be locked")
            return "-lock=false"
        if config.no_lock:
            self.printer.normal("Request for no-lock cannot be granted")
        else:
            self.printer.normal("State will be locked")
        return ""

    def _build_debug_statement(self, config: CommandConfig) -> str:
        """Build the debug statement"""
        if not config.debug:
            return ""

        self.printer.normal(
            "Running in debug mode, the following files will be created:"
        )
        self.printer.normal("- terragrunt-debug-all-inputs.json: all collected inputs")
        self.printer.normal(
            "- terragrunt-debug.tfvars.json: all relevant inputs passed to the module"
        )

        os.environ["TG_INPUTS_DEBUG"] = "true"
        return "--log-level debug --inputs-debug"

    def _build_planfile_statement(self, config: CommandConfig) -> str:
        """Build the planfile statement"""
        if config.command == "plan":
            return f"-out={self.PLANFILE_NAME}"
        if config.planfile and config.command in ["apply", "destroy"]:
            return self.PLANFILE_NAME
        return ""

    def _build_run_all_components(
        self, config: CommandConfig, components: CommandComponents
    ):
        """Build components for run-all mode"""
        components.all_stmt = "--all"
        components.interactive_stmt = (
            "--non-interactive" if config.non_interactive else ""
        )
        components.ignore_deps_stmt = (
            "--queue-exclude-external"
            if config.exclude_external_dependencies
            else "--queue-include-external"
        )
        components.include_dir_stmt = (
            f'--queue-strict-include --queue-include-dir {" --queue-include-dir ".join(shlex.quote(dir) for dir in config.include_dirs)}'
            if config.include_dirs
            else ""
        )
        components.exclude_dir_stmt = (
            f'--queue-exclude-dir {" --queue-exclude-dir ".join(shlex.quote(dir) for dir in config.exclude_dirs)}'
            if config.exclude_dirs
            else ""
        )

    def _build_run_components(
        self, config: CommandConfig, components: CommandComponents
    ):
        """Build components for single run mode"""
        components.update_stmt = "--source-update" if config.update else ""
        components.auto_approve_stmt = (
            "--auto-approve"
            if not config.no_auto_approve and config.command in TG_RW_COMMANDS
            else ""
        )
        components.working_dir_stmt = (
            f"--working-dir {config.working_dir}" if config.working_dir else ""
        )

    def _assemble_final_command(
        self, config: CommandConfig, components: CommandComponents
    ) -> str:
        """Assemble the final command from components"""
        if config.command == "clean":
            return self.COMMAND_TEMPLATES["clean"]

        # Determine which template to use based on run mode
        use_run_all = bool(components.all_stmt)

        if use_run_all:
            # Build run-all command - following the original structure more closely
            base_parts = [
                "terragrunt run",
                components.all_stmt,
                components.update_stmt,
                components.interactive_stmt,
                components.ignore_deps_stmt,  # This was missing!
                components.debug_stmt,
                components.working_dir_stmt,
                components.include_dir_stmt,
                components.exclude_dir_stmt,
                "--",
                config.command,
            ]

            base_command = " ".join(filter(None, base_parts))

            # Add terraform arguments
            terraform_args = [
                components.auto_approve_stmt,
                components.upgrade_stmt,
                components.planfile_stmt,
                components.lock_stmt,
            ]

            terraform_args = [arg for arg in terraform_args if arg]

            if terraform_args:
                full_command = f"{base_command} {' '.join(terraform_args)}"
            else:
                full_command = base_command

        else:
            # Build run-all command - following the original structure more closely
            base_parts = [
                "terragrunt run",
                components.update_stmt,
                components.debug_stmt,
                components.working_dir_stmt,
                "--",
                config.command,
            ]

            base_command = " ".join(filter(None, base_parts))

            # Add terraform arguments
            terraform_args = [
                components.auto_approve_stmt,
                components.upgrade_stmt,
                components.planfile_stmt,
                components.lock_stmt,
            ]

            terraform_args = [arg for arg in terraform_args if arg]

            if terraform_args:
                full_command = f"{base_command} {' '.join(terraform_args)}"
            else:
                full_command = base_command

        # Add additional terragrunt args if any
        if components.tg_args_statement:
            full_command = f"{full_command} {components.tg_args_statement}"

        # Clean up multiple spaces
        full_command = re.sub(r" +", " ", full_command).strip()

        if self.printer.print_verbose:
            self.printer.success(f"Full command to execute:\n❯ {full_command}")

        return full_command
