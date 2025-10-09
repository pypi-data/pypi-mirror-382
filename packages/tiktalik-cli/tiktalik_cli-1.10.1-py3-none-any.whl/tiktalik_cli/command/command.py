"""Module tiktalik_cli.command.command"""

import os
# Copyright (c) 2013 Techstorage sp. z o.o.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

from tiktalik import TiktalikAuthConnection


class CommandError(Exception):
    """Command threw an error"""


class CommandAborted(Exception):
    """Command aborted"""


@dataclass
class ProxyDetails:
    http_proxy: Optional[str]
    https_proxy: Optional[str]


def lookup_proxy_settings() -> ProxyDetails:
    details = ProxyDetails(http_proxy=None, https_proxy=None)
    if os.environ.get("HTTP_PROXY") is not None:
        details.http_proxy = os.environ.get("HTTP_PROXY")
    if os.environ.get("http_proxy") is not None:
        details.http_proxy = os.environ.get("http_proxy")
    if os.environ.get("HTTPS_PROXY") is not None:
        details.https_proxy = os.environ.get("HTTPS_PROXY")
    if os.environ.get("https_proxy") is not None:
        details.https_proxy = os.environ.get("https_proxy")

    return details


class Command(ABC):
    """Basic command"""

    def __init__(self, args, keyid, secret, connection_cls):
        self.args = args
        if connection_cls is not None:
            proxy_details = lookup_proxy_settings()
            self.conn = connection_cls(
                keyid,
                secret,
                http_proxy=proxy_details.http_proxy,
                https_proxy=proxy_details.https_proxy,
            )

    @classmethod
    def add_parser(cls, parser, subparser):
        """Parse command's args"""
        return None

    @classmethod
    def get_cmd_group_name(cls):
        """Return command group"""
        return "General commands"

    @abstractmethod
    def execute(self):
        pass

    @staticmethod
    def yesno(message: str, abort=True) -> bool:
        """Listen for a yes/no answers"""
        print(message)

        answer = None
        while answer not in ("yes", "no"):
            answer = input("Please answer 'yes' or 'no' > ")

        if answer == "yes":
            return True

        if abort:
            print("Aborted")
            sys.exit(1)
        else:
            return False


class GeneralCommand(Command):
    def __init__(self, args, keyid, secret):
        super(GeneralCommand, self).__init__(args, keyid, secret, None)

    @abstractmethod
    def execute(self):
        pass


class ComputingCommand(Command):
    def __init__(self, args, keyid, secret):
        super(ComputingCommand, self).__init__(
            args, keyid, secret, TiktalikAuthConnection
        )

    @abstractmethod
    def execute(self):
        pass

    @classmethod
    def get_cmd_group_name(cls):
        return "Computing commands"


class ComputingImageCommand(ComputingCommand):
    @abstractmethod
    def execute(self):
        pass

    @classmethod
    def get_cmd_group_name(cls):
        return "Computing image commands"


class ComputingNetworkCommand(ComputingCommand):
    @abstractmethod
    def execute(self):
        pass

    @classmethod
    def get_cmd_group_name(cls):
        return "Computing network commands"
