#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import copy

import pendulum
from coshiota.tools import log_traceback

from coshed_model.documents import JSONDocumentOnS3Controller


class Cellule(list):
    """
    >>> c = Cellule("x", pendulum.datetime(2021, 8, 8))
    >>> c.value
    'x'
    >>> c.dt
    DateTime(2021, 8, 8, 0, 0, 0, tzinfo=Timezone('+00:00'))
    >>> import orjson
    >>> orjson.dumps(c)
    b'["2021-08-08T00:00:00+00:00","x"]'
    """

    def __init__(self, value, dt=None, **kwargs):
        if dt is None:
            dt = pendulum.now().to_rfc3339_string()

        if not isinstance(dt, str):
            dt_str = dt.to_rfc3339_string()
        else:
            dt_str = dt

        list.__init__(self, (dt_str, value))

    @property
    def value(self):
        return self[1]

    @property
    def dt(self):
        return pendulum.parse(self[0])

    def __str__(self) -> str:
        return "{!r} @{!s}".format(
            self.value, self.dt.format("YYYY-MM-DD HH:mm:ss Z")
        )


class CelluleBorked(ValueError):
    pass


class ValueOutdated(ValueError):
    pass


class PoupinCerveau(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.dirty = False

    def __setitem__(self, key, value):
        if key not in self and isinstance(value, list):
            if len(value) == 2:
                dataset = [
                    Cellule(raw_val, raw_dt) for (raw_dt, raw_val) in value
                ]

                return super().__setitem__(key, dataset)

        dt_now = pendulum.now()

        try:
            raw_dataset = self[key]
        except KeyError:
            raw_dataset = [
                (dt_now, None),
                (dt_now, None),
            ]

        dataset = [
            Cellule(raw_val, raw_dt) for (raw_dt, raw_val) in raw_dataset
        ]

        previous = dataset[0]
        current = dataset[1]

        if not previous.dt <= current.dt:
            raise CelluleBorked()

        if not current.dt <= dt_now:
            raise ValueOutdated(
                "Will not accept data prior to {!r}".format(current.dt)
            )

        if current.value != value:
            previous = current
            current = Cellule(value, dt_now)
            # print("{!s} -> {!s}".format(previous, current))
        else:
            current = Cellule(value, dt_now)
            # print("{!s} == {!s}".format(previous, current))

        self.dirty = True

        return super().__setitem__(key, (previous, current))

    def learn(self, key, value):
        try:
            self[key] = value
        except CelluleBorked:
            del self[key]
            self[key] = value
        except ValueOutdated:
            return None

        return self[key][0].dt.diff(self[key][1].dt)

    def current_value(self, key):
        return self[key][-1].value

    def previous_value(self, key):
        return self[key][0].value


class NouNou:
    version = 1
    ENVIRONMENT_BUCKET = "NOUNOU_BUCKET"
    ENVIRONMENT_KEY_DATA_KEY = "NOUNOU_DATA_KEY"

    def __init__(self, data_key=None, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.maternelle = dict()
        self.data_key = data_key
        self.bucket = os.environ.get(self.ENVIRONMENT_BUCKET, "poupin")
        self.region_name = kwargs.get("region_name")
        self.changed_items = set()

        if self.data_key is None:
            self.data_key = os.environ.get(self.ENVIRONMENT_KEY_DATA_KEY)

        if self.data_key:
            self.load()

    def load(self, data_key=None):
        self.changed_items = set()
        self.maternelle = dict()

        if data_key:
            self.data_key = data_key

        if self.data_key:
            self.log.debug(
                "Loading data from {!r} using data key {!r}".format(
                    self.bucket, self.data_key
                )
            )
            persistence_control = JSONDocumentOnS3Controller(
                bucket_name=self.bucket, region_name=self.region_name
            )
            raw_data = dict()

            try:
                raw_data = persistence_control[self.data_key]
            except KeyError:
                pass

            try:
                #: transform raw data to instances of ``PoupinCerveau``
                #: and ``Cellule``
                for enfant, enfant_v in raw_data["maternelle"].items():
                    self.maternelle[enfant] = PoupinCerveau()
                    for k, v in enfant_v.items():
                        self.maternelle[enfant][k] = v
            except Exception as exc:
                log_traceback(
                    "Failed to transform raw data!", exc, uselog=self.log
                )
        else:
            self.log.warning("No data key!")

    def persist(self):
        changed_items = copy.deepcopy(self.changed_items)

        if self.data_key:
            for enfant, x in self.maternelle.items():
                if x.dirty:
                    self.log.debug("{!r} is Dirrrty".format(enfant))
                    self.changed_items.add(enfant)
                    changed_items.add(enfant)

            if self.changed_items:
                self.log.info(
                    "Changed: {!s}".format(
                        ", ".join(sorted(self.changed_items))
                    )
                )
                persistence_control = JSONDocumentOnS3Controller(
                    bucket_name=self.bucket, region_name=self.region_name
                )
                data = dict(
                    version=self.version,
                    dt=pendulum.now().to_rfc3339_string(),
                    maternelle=self.maternelle,
                )

                persistence_control[self.data_key] = data
                self.changed_items = set()
            else:
                self.log.debug("No persisting needed")
        else:
            self.log.warning("No data key!")

        return changed_items

    def forget(self, enfant, key):
        try:
            del self.maternelle[enfant][key]
            self.changed_items.add(enfant)
        except KeyError:
            pass

    def current_dict(self, enfant):
        current_data = dict()

        for key, data in self.maternelle[enfant].items():
            current_data[key] = data[1].value

        return current_data

    def teach(self, enfant, key, value):
        try:
            self.maternelle[enfant]
        except KeyError:
            self.maternelle[enfant] = PoupinCerveau()

        self.maternelle[enfant].learn(key, value)

    def teach_static(self, enfant, key, value):
        try:
            self.maternelle[enfant]
        except KeyError:
            self.maternelle[enfant] = PoupinCerveau()

        try:
            cv = self.maternelle[enfant].current_value(key)
            if cv != value:
                self.maternelle[enfant].learn(key, value)
        except KeyError:
            self.maternelle[enfant].learn(key, value)


if __name__ == "__main__":
    import doctest

    (FAILED, SUCCEEDED) = doctest.testmod()
    print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
