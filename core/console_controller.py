#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.contract.console_safe_methods import ConsoleSafeMethods


class ConsoleController:
    def __init__(self, logger):
        self.logger = logger

# Todo: move here operate_with_safe / operate_with_contract / operate_with_console