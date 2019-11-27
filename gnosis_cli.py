#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Prompt Toolkit Packages
from core.console_engine import GnosisConsoleEngine
from safe_init_scenario_script import gnosis_py_init_scenario

# Init Scenario with Random Safe with Setup (Pre-Loaded Contracts)
contract_artifacts_assests = gnosis_py_init_scenario()

# Init GNOSIS CLI
gnosis_console_engine = GnosisConsoleEngine()
gnosis_console_engine.load_contract_artifacts(contract_artifacts_assests)
gnosis_console_engine.run_console_session()
