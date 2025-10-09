#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import tempfile
import re
import warnings

from pydantic import BaseSettings

PATTERN_MAC_STRIPPED = r"^[a-f0-9]{12}$"
REGEX_MAC_STRIPPED = re.compile(PATTERN_MAC_STRIPPED)

PATTERN_VALID_HEX = r"^[a-f0-9]{4,}$"
REGEX_VALID_HEX = re.compile(PATTERN_VALID_HEX)

PATTERN_RPI_SERIAL_HEX = r"^[a-f0-9]{8}$"
REGEX_RPI_SERIAL_HEX = re.compile(PATTERN_RPI_SERIAL_HEX, re.I)

PATTERN_WIFI_HOST = r"^192\.168\.205\.\d+$"
REGEX_WIFI_HOST = re.compile(PATTERN_WIFI_HOST)

WIFI_GW_FAKE_MAC = "baaaaaadc0de"


class Settings(BaseSettings):
    edge_domain: str = "example.com"


CONFIGURATION = Settings()

if CONFIGURATION.edge_domain == "example.com":
    warnings.warn(f"Edge Domain is {CONFIGURATION.edge_domain!r}!")


def valid_colon_separated_mac_addr_or_bust(mac_addr):
    """
    Validate that value contains a valid colon separated MAC address.

    Args:
        mac_addr (str): alleged MAC address

    Returns:
        tuple: stripped address, portions, vendor prefix

    >>> valid_colon_separated_mac_addr_or_bust("")
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 16: ''
    >>> valid_colon_separated_mac_addr_or_bust("00:30:18:09:c6:b2")
    ('00301809c6b2', [0, 48, 24, 9, 198, 178], '00:30:18')
    >>> valid_colon_separated_mac_addr_or_bust("00:30:18:09:c6:b2")
    ('00301809c6b2', [0, 48, 24, 9, 198, 178], '00:30:18')
    >>> valid_colon_separated_mac_addr_or_bust("00-30-18-09-c6-b2")
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 16: '00-30-18-09-c6-b2'
    >>> valid_colon_separated_mac_addr_or_bust("ba:aa:aa:ad:c0:de")
    ('baaaaaadc0de', [186, 170, 170, 173, 192, 222], 'ba:aa:aa')
    """
    mac_addr = mac_addr.lower()
    mac_portions = [int(x, 16) for x in mac_addr.split(":")]

    mac_stripped = "".join(["{:02x}".format(x) for x in mac_portions])
    vendor_prefix = ":".join(["{:02x}".format(x) for x in mac_portions[:3]])

    assert REGEX_MAC_STRIPPED.match(mac_stripped) is not None

    return mac_stripped, mac_portions, vendor_prefix


class RemoteBerryDataMismatch(ValueError):
    pass


class RemoteBerryBadData(ValueError):
    pass


class RemoteBerryIdentity:
    """
    Raspberry Pi device identity model class.
    """

    def __init__(self, in_data, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.configuration_data_path = kwargs.get(
            "configuration_data_path", tempfile.gettempdir()
        )
        self.data = dict(identity=None, rpi_serial=None, gw_mac=None)
        self._in_data = in_data

        try:
            self._parse()
        except Exception as exc:
            self.log.warning(exc)

    def _parse(self):
        try:
            self.data["identity"] = self._in_data["identity"]
        except KeyError:
            pass

        try:
            self.data["rpi_serial"] = self._in_data["otp"]["rpi_serial"]
            assert REGEX_VALID_HEX.match(self.data["rpi_serial"]) is not None
        except (KeyError, AssertionError, TypeError):
            pass

        try:
            self.data["gw_mac"], _, _ = valid_colon_separated_mac_addr_or_bust(
                self._in_data["gateway"]["mac_addr"]
            )
            assert REGEX_VALID_HEX.match(self.data["gw_mac"]) is not None
        except (KeyError, AssertionError, TypeError):
            pass

        if self.data["identity"]:
            value = self.data["identity"]["gw_mac"]

            if not REGEX_MAC_STRIPPED.match(value):
                self.log.warning("Tainted: mac_stripped={!r}".format(value))

        if self.data["identity"] and not self.data["rpi_serial"]:
            try:
                self.data["rpi_serial"] = self._in_data["identity"][
                    "rpi_serial"
                ]
            except KeyError:
                pass

        if self.data["gw_mac"] and self.data["identity"]:
            if self.data["gw_mac"] != self.data["identity"].get("gw_mac"):
                self.log.warning(
                    "Tainted: gw_mac={!r} identity/gw_mac={!r}".format(
                        self.data["gw_mac"], self.data["identity"]["gw_mac"]
                    )
                )

    def __str__(self):
        portions = [
            "<{:s}".format(self.__class__.__name__),
            (not self.sufficient and " (INSUFFICIENT)" or ""),
        ]

        try:
            portions.append(" {:s}".format(self.inventory_hostname))
        except Exception:
            pass

        if self.rpi_serial:
            portions.append(" rpi_serial={:s}".format(self.rpi_serial))

        if self.gw_mac:
            portions.append(" gw_mac={:s}".format(self.gw_mac))

        try:
            portions.append(
                " serial={!r}".format(self.identity["serial_number"])
            )
        except Exception:
            pass

        portions.append(">")

        return "".join(portions)

    @property
    def sufficient(self):
        return {self.rpi_serial, self.gw_mac} != {None}

    @property
    def data_path(self):
        if self.gw_mac:
            return os.path.join(self.configuration_data_path, self.gw_mac)

        if not self.data["rpi_serial"]:
            raise RemoteBerryBadData("rpi_serial")

        return self.rpi_data_path

    @property
    def rpi_data_path(self):
        if self.rpi_serial:
            return os.path.join(self.configuration_data_path, self.rpi_serial)

        return None

    @property
    def storage_key(self):
        if self.rpi_serial:
            return self.rpi_serial

        return None

    @property
    def inventory_hostname(self):
        if not self.identity.get("inventory_hostname"):
            raise RemoteBerryBadData("inventory_hostname")

        if self.identity.get("inventory_hostname").strip().startswith("{{"):
            raise RemoteBerryBadData("inventory_hostname")

        return self.identity["inventory_hostname"]

    @property
    def inventory_hostname_for_storage(self):
        if self.gw_mac == WIFI_GW_FAKE_MAC:
            return f"{self.rpi_serial}.{CONFIGURATION.edge_domain}"

        if self.inventory_hostname.startswith("192.168."):
            return f"{self.rpi_serial}.{CONFIGURATION.edge_domain}"

        return self.inventory_hostname

    @property
    def gw_mac(self):
        return self.data["gw_mac"]

    @property
    def identity(self):
        if not self.data["identity"]:
            raise RemoteBerryBadData("identity")

        return self.data["identity"]

    @property
    def rpi_serial(self):
        return self.data["rpi_serial"]


if __name__ == "__main__":
    import doctest

    (FAILED, SUCCEEDED) = doctest.testmod()
    print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
