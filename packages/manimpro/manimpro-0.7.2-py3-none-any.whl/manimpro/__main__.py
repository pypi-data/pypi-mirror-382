from __future__ import annotations

import click
import cloup

from manimpro import __version__
from manimpro._config import cli_ctx_settings, console
from manimpro.cli.cfg.group import cfg
from manimpro.cli.checkhealth.commands import checkhealth
from manimpro.cli.default_group import DefaultGroup
from manimpro.cli.init.commands import init
from manimpro.cli.plugins.commands import plugins
from manimpro.cli.preview.commands import preview_command
from manimpro.cli.render.commands import render
from manimpro.cli.wizard.commands import wizard_group
from manimpro.constants import EPILOG


def show_splash(ctx: click.Context, param: click.Option, value: str | None) -> None:
    """When giving a value by console, show an initial message with the ManimPro
    version before executing any other command: ``ManimPro vA.B.C``.

    Parameters
    ----------
    ctx
        The Click context.
    param
        A Click option.
    value
        A string value given by console, or None.
    """
    if value:
        console.print(f"ManimPro [green]v{__version__}[/green]\n")


def print_version_and_exit(
    ctx: click.Context, param: click.Option, value: str | None
) -> None:
    """Same as :func:`show_splash`, but also exit when giving a value by
    console.

    Parameters
    ----------
    ctx
        The Click context.
    param
        A Click option.
    value
        A string value given by console, or None.
    """
    show_splash(ctx, param, value)
    if value:
        ctx.exit()


@cloup.group(
    context_settings=cli_ctx_settings,
    cls=DefaultGroup,
    default="render",
    no_args_is_help=True,
    help="Animation engine for explanatory math videos.",
    epilog="See 'manimpro <command>' to read about a specific subcommand.\n\n"
    "Note: the subcommand 'manimpro render' is called if no other subcommand "
    "is specified. Run 'manimpro render --help' if you would like to know what the "
    f"'-ql' or '-p' flags do, for example.\n\n{EPILOG}",
)
@cloup.option(
    "--version",
    is_flag=True,
    help="Show version and exit.",
    callback=print_version_and_exit,
    is_eager=True,
    expose_value=False,
)
@click.option(
    "--show-splash/--hide-splash",
    is_flag=True,
    default=True,
    help="Print splash message with version information.",
    callback=show_splash,
    is_eager=True,
    expose_value=False,
)
@cloup.pass_context
def main(ctx: click.Context) -> None:
    """The entry point for ManimPro.

    Parameters
    ----------
    ctx
        The Click context.
    """
    pass


main.add_command(checkhealth)
main.add_command(cfg)
main.add_command(plugins)
main.add_command(init)
main.add_command(preview_command)
main.add_command(render)
main.add_command(wizard_group)

if __name__ == "__main__":
    main()
