#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pendulum

from coshed_model.spof_client import SPOFClient
from coshed_model.spof_client import DEFAULT_ENVIRONMENT, ENVIRONMENT_ITEMS


class SPOFNotificationNotification(SPOFClient):
    def __init__(self, hostname, *args, **kwargs):
        super().__init__(hostname, *args, **kwargs)

    def post_machine_message(
        self, occurrence, serial_number, content, env_name=None, **kwargs
    ):
        if env_name is None:
            env_name = DEFAULT_ENVIRONMENT
        assert env_name in ENVIRONMENT_ITEMS
        sender = kwargs.get("sender", "ALARM_MONITORING_FEATURE")
        category = kwargs.get("category", "IndexAlarm")
        payload = {
            "notificationText": content,
            "source": sender,
            "messageCreatedTimestamp": pendulum.now().to_rfc3339_string(),
            "sourceEventTimestamp": occurrence.to_rfc3339_string(),
            "category": category,
        }
        s_data = self._session_store[env_name]
        the_url = "{base_url}/v1/{serial_number}/MONITORING_SERVICE/PostMachineMessage".format(
            base_url=s_data["base_url"], serial_number=serial_number
        )

        try:
            req = s_data["session"].post(the_url, json=payload)

            if req.status_code != 200:
                self.log.warning(
                    "Got HTTP Status Code {!r}".format(req.status_code)
                )

            return req.status_code == 200
        except Exception as exc:
            self.log.error(exc)

        return False


if __name__ == "__main__":
    snn = SPOFNotificationNotification(
        "ix-api-manager", api_key_prefix="SPOF_SNN_API_KEY"
    )
    snn.post_machine_message(
        pendulum.now().subtract(minutes=17),
        "42424242",
        "<script>alert('gotcha');</script>",
        env_name="dev",
        category="SuperFieserAlarm",
    )
