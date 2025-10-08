# Copyright NTESS. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

import argparse
import webbrowser

from ..hookspec import hookimpl
from ..types import CanarySubcommand


@hookimpl
def canary_subcommand() -> CanarySubcommand:
    return Docs()


class Docs(CanarySubcommand):
    name = "docs"
    description = "open canary documentation in a web browser"

    def execute(self, args: "argparse.Namespace") -> int:
        webbrowser.open("https://canary-wm.readthedocs.io/en/production/")
        return 0
