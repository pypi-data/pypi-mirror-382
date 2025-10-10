#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import logging

import pendulum
import orjson

from coshed_model.ansible_remote_identity import RemoteBerryIdentity
from coshed_model.ansible_remote_identity import REGEX_WIFI_HOST

COUCHDB_INTERNAL_KEYS = ("_id", "_rev")

#: key of key/value pairs holding dataset
DATA_KEYS = (
    "tags",
    "host",
    "dump",
    "location",
    "ping",
    "snapshot",
    "ring",
    "time_out",
    "taints",
    "flags",
)

#: key of the key/value pairs keeping track on when datasets WERE updated
PORTIONS_DT_KEY = "portions_dt"

#: key of the key/value pairs keeping track on when datasets SHOULD be updated
PORTIONS_NEXT_DT_KEY = "portions_next_dt"

#: current version of the data model specification
SPECIFICATION_VERSION = 10

#: automatic refreshing of datasets thresholds
AUTOMATIC_REFRESH_THRESHOLDS = {
    "_default": pendulum.duration(days=1),
    "_empty_value": pendulum.duration(hours=9),
    "ping": pendulum.duration(minutes=9),
    "location": pendulum.duration(days=7),
    "dump": pendulum.duration(minutes=30),
    "snapshot": pendulum.duration(minutes=30),
}


def mangled_data_portion(key, data):
    log = logging.getLogger(__name__)
    log.debug("<<< {!s}: {!r}".format(key, data))

    if data is None:
        return None

    del_keys = set(["dt"]) | set(COUCHDB_INTERNAL_KEYS)

    if key == "location":
        del_keys |= {"objectId", "internalID", "imageUrl", "contacts"}

        for data_key in data.keys():
            if not data[data_key]:
                del_keys.add(data_key)
    elif key == "host" and data.get("fishy") is None:
        data["is_fishy"] = False
        try:
            if REGEX_WIFI_HOST.match(data["inventory_hostname"]):
                data["is_fishy"] = True
        except Exception as exc:
            log.error(exc)

    if isinstance(data, dict):
        for del_key in del_keys:
            try:
                del data[del_key]
            except KeyError:
                pass

    log.debug(">>> {!s}: {!r}".format(key, data))

    return data


class AHMDocument(dict):
    """
    Ansible Host Metadata Document.

    >>> a = AHMDocument()
    >>> b = AHMDocument()
    >>> a == b
    True
    >>> a["x"] = 123
    >>> a.dirty
    True
    >>> not a.has_changed_portion({"something_else"})
    True
    >>> a["tags"] = ["a", "b", "c"]
    >>> a.dirrty_filthy_nasty
    {'tags'}
    >>> not a.has_changed_portion({"tags"})
    False
    >>> json_bytes = orjson.dumps(a)
    >>> len(json_bytes)
    204
    >>> set(b.keys()) == {'portions_dt', 'portions_next_dt'}
    True
    >>> len(b.keys())
    2
    >>> b.remangle()
    >>> len(b.keys()) > 2
    True
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)

        for cik in COUCHDB_INTERNAL_KEYS:
            try:
                del self[cik]
            except KeyError:
                pass

        self.dirrty_filthy_nasty = set()
        self.read_dt = copy.copy(self.dt)

        for portions_dk in (PORTIONS_DT_KEY, PORTIONS_NEXT_DT_KEY):
            try:
                self[portions_dk]
            except KeyError:
                self[portions_dk] = dict()

            if not isinstance(self[portions_dk], dict):
                self[portions_dk] = dict()

    def next_refresh_threshold(self, key):
        """
        Determine the threshold value for automatic refresh of ``key``.

        Args:
            key (str): data portion key

        Returns:
            datetime.timedelta: auto refresh threshold
        """
        if self.get(key) is None:
            return AUTOMATIC_REFRESH_THRESHOLDS["_empty_value"]
        else:
            try:
                return AUTOMATIC_REFRESH_THRESHOLDS[key]
            except KeyError:
                pass

        return AUTOMATIC_REFRESH_THRESHOLDS["_default"]

    def touch(self, portion_key=None):
        """
        Mark metadata document as **changed** storing current timestamp as
        change date.

        If ``portion_key`` is provided specifically also mark the referenced
        data portion as changed.

        Args:
            portion_key (str, optional): data portion key. Defaults to None.

        """
        self.log.debug("You can't touch this")
        u_now = pendulum.now(pendulum.UTC)
        self["dt"] = u_now.to_rfc3339_string()
        self["version"] = SPECIFICATION_VERSION

        if portion_key:
            self.dirrty_filthy_nasty.add(portion_key)
            self[PORTIONS_DT_KEY][portion_key] = self["dt"]
            threshold = self.next_refresh_threshold(portion_key)
            next_dt = u_now + threshold
            self[PORTIONS_NEXT_DT_KEY][
                portion_key
            ] = next_dt.to_rfc3339_string()

    @property
    def dirty(self):
        """
        Return indicator if metadata should be persisted.

        Returns:
            bool: ``True`` if document has changed
        """
        return self.read_dt != self.dt

    @property
    def dt(self):
        """
        Return *latest changed* datetime object.

        Returns:
            datetime.datetime: datetime of latest change. Falls back to \
                current datetime
        """
        try:
            return pendulum.parse(self["dt"])
        except KeyError:
            return pendulum.now(pendulum.UTC)

    @property
    def version(self):
        """
        Return document version

        Returns:
            int: document version. Falls back to ``0``
        """
        try:
            return self["version"]
        except KeyError:
            return 0

    @property
    def identity(self):
        """
        Return remote berry identity object

        Returns:
            RemoteBerryIdentity: identity object
        """
        return RemoteBerryIdentity(dict(identity=self["host"]))

    @property
    def equipment_id(self):
        """
        Return AIN equipment ID. Falls back to ``None``.

        Returns:
            str: AIN ID
        """
        try:
            return self["host"]["equipment_id"]
        except Exception:
            pass

        return None

    @property
    def item_id(self):
        """
        Return Thing ID.  Falls back to ``None``.

        Returns:
            str: Thing ID
        """
        try:
            return self["host"]["item_id"]
        except Exception:
            pass

        return None

    @property
    def serial_number(self):
        """
        Return Serial Number. Falls back to ``None``.

        Returns:
            str: serial number
        """
        try:
            return self["host"]["serial_number"]
        except Exception:
            pass

        return None

    @property
    def inventory_hostname(self):
        """
        Return ansible inventory hostname. Falls back to ``None``.

        Returns:
            str: ansible inventory hostname
        """
        try:
            return self["host"]["inventory_hostname"]
        except Exception:
            pass

        return None

    @property
    def is_fishy(self):
        """
        Return indicator if current metadata indicates a *fishy*
        host. This means that the host is apparently not connected
        by a genubox device.

        Returns:
            bool: Indicator if host is to be considered *fishy*
        """
        try:
            return self["host"]["is_fishy"]
        except Exception:
            pass

        return False

    def has_changed_portion(self, interest):
        return self.dirrty_filthy_nasty & interest

    def next_refresh(self, key):
        """
        Determine the next moment in time at which ``key`` may be refreshed
        automatically.

        Args:
            key (str): data portion key

        Returns:
            datetime.datetime: next auto refresh
        """
        threshold = self.next_refresh_threshold(key)
        next_dt = self.read_dt + threshold

        try:
            next_dt = pendulum.parse(self[PORTIONS_NEXT_DT_KEY][key])
        except KeyError:
            self[PORTIONS_NEXT_DT_KEY][key] = next_dt.to_rfc3339_string()
        except Exception:
            pass

        return next_dt

    def refreshable_portion(self, key):
        """
        Return indicator if data portion ``key`` may be refreshed now.

        Args:
            key (str): data portion key

        Returns:
            bool: ``True`` if data portion may be refreshed
        """
        return pendulum.now() >= self.next_refresh(key)

    def __setitem__(self, key, value):
        old_value = self.get(key)

        if key in DATA_KEYS:
            value = mangled_data_portion(key, copy.deepcopy(value))

        super().__setitem__(key, value)

        if key in DATA_KEYS and old_value != value:
            self.touch(key)

    def remangle(self):
        """
        (Re-)Apply mangling to all data portion key/value pairs.
        """
        for key in DATA_KEYS:
            self[key] = self.get(key)

    def __str__(self):
        if self.dirty:
            dirty_indicator = " DIRTY ({:s})".format(
                ", ".join(sorted(self.dirrty_filthy_nasty))
            )
        else:
            dirty_indicator = ""

        return "<{klass} {version}> {dt}{dirty_indicator}".format(
            klass=self.__class__.__name__,
            version=self.version,
            dt=self.dt,
            dirty_indicator=dirty_indicator,
        )

    def __eq__(self, other):
        for key in DATA_KEYS:
            if self.get(key) != other.get(key):
                return False

        return True

    def json(self):
        return orjson.dumps(self)


if __name__ == "__main__":
    import doctest

    (FAILED, SUCCEEDED) = doctest.testmod()
    print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
