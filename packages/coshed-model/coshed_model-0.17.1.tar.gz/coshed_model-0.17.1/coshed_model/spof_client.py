#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

import requests
from coshed_model.naming import cfapp_base_url

ENVIRONMENT_ITEMS = ("prod", "dev", "qa")

DEFAULT_ENVIRONMENT = "dev"

DUMMY_API_KEY = (
    "you are superior in only one respect -- you are better at dying"
)


class SPOFClient:
    def __init__(self, hostname, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.api_key_prefix = kwargs.get("api_key_prefix", "SPOF_API_KEY")
        self.env_name = kwargs.get("env_name", "prod")
        api_keys = dict()
        self._session_store = dict()
        self.roster = dict()

        if kwargs.get("api_keys"):
            api_keys = kwargs.get("api_keys")
        else:
            for key in ENVIRONMENT_ITEMS:
                env_key = "{:s}_{!s}".format(self.api_key_prefix, key.upper())

                if self.api_key_prefix in os.environ:
                    env_key = self.api_key_prefix
                    self.log.debug(
                        "Using {env_key!s} for {key!s}".format(
                            env_key=env_key, key=key
                        )
                    )

                try:
                    api_keys[key] = os.environ[env_key]
                except KeyError:
                    self.log.warning(
                        "No API Key for {!s} found in environment variable {!s}".format(
                            key, env_key
                        )
                    )

        for env_name in ENVIRONMENT_ITEMS:
            self.roster[env_name] = dict()
            if not api_keys.get(env_name):
                api_keys[env_name] = DUMMY_API_KEY

            session_data = dict(
                base_url=cfapp_base_url(hostname, env_name=env_name),
                session=requests.Session(),
            )
            headers = dict(
                accept="application/json", authorization=api_keys[env_name]
            )
            session_data["session"].headers.update(headers)
            # self.log.debug(session_data["session"].headers)
            self._session_store[env_name] = session_data
