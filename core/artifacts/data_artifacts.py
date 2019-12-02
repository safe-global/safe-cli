#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DataArtifacts:
    def __init__(self, logger, account_artifacts, payload_artifacts, token_artifacts, contract_artifacts):
        self.name = self.__class__.__name__
        self.logger = logger
        self.account_artifacts = account_artifacts
        self.payload_artifacts = payload_artifacts
        self.token_artifacts = token_artifacts
        self.contract_artifacts = contract_artifacts