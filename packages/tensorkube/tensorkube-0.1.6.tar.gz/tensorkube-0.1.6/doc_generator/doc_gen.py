import inspect
from pathlib import Path
from typing import List

import click

from tensorkube.services.cli import tensorkube

# this file handles automatic doc creation only for the reference section. Try to keep this as simple as possible
# also since the changes might propogate always keep an eye on the doc PR that this thing generates.

class ClickDocGenerator:
    # Blacklist for groups and commands that should be ignored
    BLACKLISTED_GROUPS = {'completion',  # example: ignore completion group
        'internal',  # example: ignore internal group
        'cluster'}

    BLACKLISTED_COMMANDS = {'test'# example: ignore version command  # example: ignore help command
    }

    def __init__(self, cli: click.Group):
        self.cli = cli

    def _format_option(self, opt: click.Option) -> str:
        """Format a single option with compact styling."""
        # Get option type
        opt_type = (f"Choice({opt.type.choices})" if isinstance(opt.type,
                                                                click.Choice) else opt.type.name.upper() if opt.type else "STRING")

        # Get default value
        default = str(opt.default) if opt.default is not None else None

        # Get the option name as it appears in CLI (with dashes)
        opt_name = opt.opts[-1]  # Use the last option name (usually the long form)

        # Split help text into main line and additional lines
        help_lines = opt.help.split('\n') if opt.help else ["No description available."]
        main_help = help_lines[0].strip()
        additional_help = [line.strip() for line in help_lines[1:] if line.strip()]

        # Format main option line
        if default:
            option_line = f"* `{opt_name} {opt_type}` [default: {default}]: {main_help}"
        else:
            option_line = f"* `{opt_name} {opt_type}`: {main_help}"

        # Add additional help lines with indentation if they exist
        if additional_help:
            option_line += "\n" + "\n".join(f"    {line}" for line in additional_help)

        return option_line

    def _format_argument(self, arg: click.Argument) -> str:
        """Format a single argument."""
        arg_type = (f"Choice({arg.type.choices})" if isinstance(arg.type,
                                                                click.Choice) else arg.type.name.upper() if arg.type else "STRING")

        # Format argument name in uppercase with angle brackets
        arg_name = f"<{arg.name.upper()}>"

        help_text = arg.help if hasattr(arg, 'help') else "No description available."
        return f"* `{arg_name}` ({arg_type}): {help_text}"

    def _should_include_command(self, cmd_name: str, cmd: click.Command) -> bool:
        """Check if command should be included in documentation."""
        if isinstance(cmd, click.Group):
            return cmd_name not in self.BLACKLISTED_GROUPS
        return cmd_name not in self.BLACKLISTED_COMMANDS

    def _format_command_help(self, cmd: click.Command, path: str = "") -> str:
        """Format help text for a command."""
        doc = cmd.help or inspect.getdoc(cmd)

        # Split docstring into main description and rest
        sections = []

        # Add the heading section for the subcommand
        sections.extend([f"## `{path}`"])

        if doc:
            # Add the main description
            doc_parts = doc.split('Examples:', 1)
            description = doc_parts[0].strip()
            sections.extend([f"{description}\n"])

            # Add Examples section if present
            if len(doc_parts) > 1:
                sections.extend(["**Examples:**\n", doc_parts[1].strip(), "\n"])
        else:
            sections.extend(["No description available.\n"])

        # Add Usage section
        sections.extend(["**Usage:**\n"])

        # Build the usage string
        usage_parts = [path]

        # Add arguments to usage
        arguments = [p for p in cmd.params if isinstance(p, click.Argument)]
        for arg in arguments:
            usage_parts.append(f"<{arg.name.upper()}>")

        # Add options indication to usage if there are options
        options = [p for p in cmd.params if isinstance(p, click.Option)]
        if options:
            usage_parts.append("[OPTIONS]")

        # Add COMMAND [ARGS]... for groups
        if isinstance(cmd, click.Group):
            usage_parts.append("COMMAND [ARGS]...")
        # join all parts
        # Join all parts with spaces
        usage_string = " ".join(usage_parts)

        # Add the usage block with bash identifier
        sections.extend([
            "```bash",
            usage_string,
            "```\n"
        ])


        # Add Arguments section if present
        arguments = [p for p in cmd.params if isinstance(p, click.Argument)]
        if arguments:
            sections.append("**Arguments:**\n")
            sections.extend([self._format_argument(arg) + "\n" for arg in arguments])

        # Add Options section
        options = [p for p in cmd.params if isinstance(p, click.Option)]
        if options or isinstance(cmd, click.Command):
            sections.append("**Options:**\n")
            sections.extend([self._format_option(opt) + "\n" for opt in options])

            # Add help option
            sections.append("* `--help BOOL` [default: false]: Show this message and exit.\n")

        # Add Commands section for groups, filtering out blacklisted commands
        if isinstance(cmd, click.Group):
            sections.append("**Commands:**\n")
            for name, subcmd in cmd.commands.items():
                if self._should_include_command(name, subcmd):
                    help_text = subcmd.help or inspect.getdoc(subcmd)
                    short_help = help_text.split('\n')[0] if help_text else "No description."
                    sections.append(f"* `{name}`: {short_help}\n")

        return "\n".join(sections)

    def generate_docs(self, output_dir: str):
        """Generate documentation for the entire CLI."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        def process_group(group: click.Group, parents: List[str] = None):
            if parents is None:
                parents = []

            current_path = " ".join([*parents, group.name])

            # Handle base group (tensorkube) commands
            if len(parents) == 0:
                # Generate separate files for direct commands, filtering blacklisted ones
                for cmd_name, cmd in group.commands.items():
                    if not isinstance(cmd, click.Group) and self._should_include_command(cmd_name, cmd):
                        cmd_path = f"{current_path} {cmd_name}"
                        content = ["---", f"title: '{cmd_path}'", f"sidebarTitle: \"{cmd_path}\"", "---\n",
                            self._format_command_help(cmd, cmd_path)]
                        filename = cmd_path.replace(" ", "_").replace("-", "_")
                        (output_path / f"{filename}.mdx").write_text("\n".join(content))

                # Generate base group file with only group info
                content = ["---", f"title: '{current_path}'", f"sidebarTitle: \"{current_path}\"", "---\n",
                    self._format_command_help(group, current_path)]
                filename = current_path.replace(" ", "_").replace("-", "_")
                (output_path / f"{filename}.mdx").write_text("\n".join(content))

            # Handle subgroups (tensorkube <sub-group>)
            elif len(parents) == 1:
                # Skip blacklisted groups
                if not self._should_include_command(group.name, group):
                    return
                content = ["---", f"title: '{current_path}'", f"sidebarTitle: \"{current_path}\"", "---\n",
                    self._format_command_help(group, current_path)]

                # Add subcommand documentation for this group, filtering blacklisted ones
                for cmd_name, cmd in group.commands.items():
                    if self._should_include_command(cmd_name, cmd):
                        cmd_path = f"{current_path} {cmd_name}"
                        content.append("\n" + self._format_command_help(cmd, cmd_path))

                filename = current_path.replace(" ", "_").replace("-", "_")
                (output_path / f"{filename}.mdx").write_text("\n".join(content))

            # Process subgroups, filtering blacklisted ones
            for cmd_name, cmd in group.commands.items():
                if isinstance(cmd, click.Group) and self._should_include_command(cmd_name, cmd):
                    process_group(cmd, [*parents, group.name])

        process_group(self.cli)


if __name__ == '__main__':
    generator = ClickDocGenerator(tensorkube)
    generator.generate_docs("docs/commands")
