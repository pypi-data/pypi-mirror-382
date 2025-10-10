import click
from .constants import APP_NAME
from .constants import APP_FULLNAME

def get_params_usage(cmd, ctx):
    args = []
    opts = []
    for p in cmd.params:
        if isinstance(p, click.Argument):
            name = p.name.upper()
            if p.required:
                args.append(name)
            else:
                args.append(f"[{name}]")
        elif isinstance(p, click.Option):
            opt_str = p.opts[0] if p.opts else f"--{p.name}"
            if p.is_flag:
                opts.append(f"{opt_str}")
            else:
                dest = p.dest.upper()
                opts.append(f"{opt_str} {dest}")
    param_str = " ".join(args)
    if opts:
        param_str += " " + " ".join(opts)
    if not param_str:
        param_str = ""
    return param_str

class CleanGroup(click.Group):
    def format_help(self, ctx, formatter):
        header = APP_NAME if not ctx.command_path else f"{ctx.command_path}"
        if header.find("python") == 0:
            header = APP_NAME
        formatter.write_text(header + " - " + APP_FULLNAME)
        formatter.write_paragraph()
        formatter.write_heading("Usage")
        usage = header
        if self.commands:
            usage += " COMMAND [ARGS]..."
        formatter.write_text(usage)
        formatter.write_paragraph()
        if self.commands:
            formatter.write_heading("Commands")
            self._format_command_usages(ctx, formatter, current_path=header)

    def _format_command_usages(self, ctx, formatter, current_path):
        commands = self.list_commands(ctx)
        for subcommand in commands:
            cmd = self.get_command(ctx, subcommand)
            new_path = f"{current_path} {subcommand}"
            if isinstance(cmd, click.Group):
                sub_ctx = click.Context(cmd, parent=ctx)
                cmd._format_command_usages(sub_ctx, formatter, new_path)
            else:
                sub_ctx = click.Context(cmd, parent=ctx)
                params = get_params_usage(cmd, sub_ctx)
                full_usage = f"{new_path} {params}".strip()
                short_help = cmd.short_help or (cmd.__doc__.split('\n')[0].strip() if cmd.__doc__ else '')
                if short_help:
                    full_usage = f"{full_usage:<56}{short_help}"
                formatter.write_text(full_usage + "\n")