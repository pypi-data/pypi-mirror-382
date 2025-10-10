#!/usr/bin/env python
# -*- coding: utf-8 -*-
from coshed_model.spof_client import SPOFClient
from coshed_model.spof_client import DEFAULT_ENVIRONMENT, ENVIRONMENT_ITEMS


class SPOFRoster(SPOFClient):
    def __init__(self, hostname, *args, **kwargs):
        super().__init__(hostname, *args, **kwargs)
        self.arn_prefix = kwargs.get("arn_prefix", "OH:IF:ONLY:WE:KNEW:")

    def fetch(self, serial_number, env_name=None):
        data = list()
        if env_name is None:
            env_name = DEFAULT_ENVIRONMENT
        s_data = self._session_store[env_name]
        the_url = "{base_url}/v1/{serial_number}/NOTIFICATION_SERVICE/NotificationsForMachine".format(
            base_url=s_data["base_url"], serial_number=serial_number
        )

        try:
            req = s_data["session"].get(the_url)

            for raw in req.json():
                item = dict(
                    topic_arn=self.arn_prefix + raw["id"],
                    user_id=raw["userId"],
                )
                # self.log.debug(raw)
                data.append(item)
        except Exception:
            return None

        return data

    def __getitem__(self, key):
        if isinstance(key, tuple):
            env_name, item_key = key
        else:
            env_name = DEFAULT_ENVIRONMENT
            item_key = key

        if item_key not in self.roster[env_name]:
            value = self.fetch(item_key, env_name=env_name)
            if value is not None:
                self[key] = value

        return self.roster[env_name][item_key]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            env_name, item_key = key
        else:
            env_name = DEFAULT_ENVIRONMENT
            item_key = key

        self.roster[env_name][item_key] = value

    def get_user_items(self, serial_number, env_name):
        assert env_name in ENVIRONMENT_ITEMS

        try:
            return self[(env_name, serial_number)]
        except KeyError:
            return []
