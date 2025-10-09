# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Query a program's list of features."""

from __future__ import annotations

import dataclasses
import sys
from typing import Final

import click


try:
    import simplejson as js
except ImportError:
    import json as js  # type: ignore[no-redef]

from . import defs
from . import expr as fexpr
from . import obtain
from . import parser as fparser
from . import version as fver


@dataclasses.dataclass(frozen=True)
class Config:
    """Runtime configuration for this program."""

    args: list[str]
    display_version: bool
    features_prefix: str
    option_name: str
    output_format: str

    program: str = "(unknown)"


def arg_version(_ctx: click.Context, _self: click.Parameter, value: bool) -> bool:  # noqa: FBT001
    """Display program version information."""
    if not value:
        return value

    print(f"feature-check {defs.VERSION}")
    sys.exit(0)


def arg_features(_ctx: click.Context, _self: click.Parameter, value: bool) -> bool:  # noqa: FBT001
    """Display program features information."""
    if not value:
        return value

    print(f"{defs.DEFAULT_PREFIX}feature-check={defs.VERSION} single=1.0 list=1.0 simple=1.0")
    sys.exit(0)


def output_tsv(data: dict[str, fver.Version]) -> None:
    """List the obtained features as tab-separated name/value pairs."""
    for feature in sorted(data.keys()):
        print(f"{feature}\t{data[feature].value}")


def output_json(data: dict[str, fver.Version]) -> None:
    """List the obtained features as a JSON object."""
    print(
        js.dumps(
            {name: value.value for name, value in data.items()},
            sort_keys=True,
            indent=2,
        ),
    )


OUTPUT = {"tsv": output_tsv, "json": output_json}


def process(mode: defs.Mode, cfg: Config, data: dict[str, fver.Version]) -> None:
    """Perform the requested feature-check operation."""
    match mode:
        case defs.ModeList():
            OUTPUT[cfg.output_format](data)

        case defs.ModeSingle(feature, _):
            if feature in data:
                if cfg.display_version:
                    print(data[feature].value)
                sys.exit(0)
            else:
                sys.exit(1)

        case defs.ModeSimple(ast):
            res: Final = ast.evaluate(data)
            if not isinstance(res, fexpr.ResultBool):
                sys.exit(f"Internal error: did not expect a {type(res).__name__} object")
            sys.exit(not res.value)

        case _:
            sys.exit(f"Internal error: process(mode={mode!r}, cfg={cfg!r}, data={data!r}")


@click.command(name="feature-check")
@click.help_option("--help", "-h")
@click.option(
    "--version",
    "-V",
    is_flag=True,
    is_eager=True,
    callback=arg_version,
    help="display program version information and exit",
)
@click.option(
    "--features",
    is_flag=True,
    is_eager=True,
    callback=arg_features,
    help="display supported features and exit",
)
@click.option(
    "-v",
    "--display-version",
    is_flag=True,
    help="display the feature version",
)
@click.option(
    "-P",
    "--features-prefix",
    type=str,
    default=defs.DEFAULT_PREFIX,
    help="the features prefix in the program output",
)
@click.option(
    "-l",
    "--list",
    "opt_list",
    is_flag=True,
    help="list the features supported by a program",
)
@click.option(
    "-O",
    "--option-name",
    type=str,
    default=defs.DEFAULT_OPTION,
    help="the query-features option to pass",
)
@click.option(
    "-o",
    "--output-format",
    type=click.Choice(sorted(OUTPUT.keys())),
    default=defs.DEFAULT_OUTPUT_FMT,
    help="specify the output format for the list",
)
@click.argument("program", type=str)
@click.argument("feature", type=str, required=False)
@click.argument("op", type=str, required=False)
@click.argument("feature_version", type=str, required=False, metavar="VERSION")
@click.pass_context
def main(  # noqa: PLR0913  # yep, we accept a lot of command-line options
    ctx: click.Context,
    *,
    program: str,
    feature: str | None,
    op: str | None,
    display_version: bool,
    feature_version: str | None,
    features: bool,
    features_prefix: str,
    opt_list: bool,
    option_name: str,
    output_format: str,
    version: bool,
) -> None:
    """Parse command-line arguments, do things."""

    def parse_mode() -> defs.Mode:
        """Determine the mode of operation."""
        if opt_list:
            return defs.ModeList()

        if not cfg.args:
            ctx.fail("No feature specified")
        expr: Final = " ".join(cfg.args)
        try:
            return fparser.parse_expr(expr)
        except fparser.ParseError:
            ctx.fail("Only querying a single feature supported so far")

    if features or version:
        ctx.fail(f"How did we get to main() with {features=!r} and {version=!r}?")

    cfg: Final = Config(
        program=program,
        args=[value for value in [feature, op, feature_version] if value is not None],
        display_version=display_version,
        features_prefix=features_prefix,
        option_name=option_name,
        output_format=output_format,
    )

    mode: Final = parse_mode()

    try:
        data: Final = obtain.obtain_features(cfg.program, cfg.option_name, cfg.features_prefix)
    except obtain.ObtainError as exc:
        sys.exit(exc.code)

    process(mode, cfg, data)


if __name__ == "__main__":
    main()
