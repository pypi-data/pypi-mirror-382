#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re

PATTERN_INVALID_CHAR = r"[^a-z0-9]"
REGEX_INVALID_CHAR = re.compile(PATTERN_INVALID_CHAR)

PATTERN_BLACKLISTED = r"^([nN][\-\\\/][aA])$"
REGEX_BLACKLISTED = re.compile(PATTERN_BLACKLISTED)

PATTERN_MAC_STRIPPED = r"^[a-f0-9]{12}$"
REGEX_MAC_STRIPPED = re.compile(PATTERN_MAC_STRIPPED)

PATTERN_VALID_HEX = r"^[a-f0-9]{4,}$"
REGEX_VALID_HEX = re.compile(PATTERN_VALID_HEX)


def valid_mac_addr_or_bust(mac_addr):
    """
    Make sure that provided value is a valid MAC address and return its
    stripped value, portions and vendor prefix

    Args:
        mac_addr (str): MAC address

    Returns:
        tuple: stripped value, portions, vendor prefix

    >>> valid_mac_addr_or_bust("00:30:de:ad:be:ef")
    ('0030deadbeef', [0, 48, 222, 173, 190, 239], '00:30:de')
    """
    mac_addr = mac_addr.lower()
    mac_portions = [int(x, 16) for x in mac_addr.split(":")]

    mac_stripped = "".join(["{:02x}".format(x) for x in mac_portions])
    vendor_prefix = ":".join(["{:02x}".format(x) for x in mac_portions[:3]])

    assert REGEX_MAC_STRIPPED.match(mac_stripped) is not None

    return mac_stripped, mac_portions, vendor_prefix


class BlacklistedError(ValueError):
    pass


def mangled_dns_value(value):
    """
    Mangle a serial number value in such ways that it can be used
    as a hostname in DNS.

    Args:
        value (str): input value

    Returns:
        str: mangled value

    >>> mangled_dns_value('')
    Traceback (most recent call last):
        ...
    ValueError: '' is an invalid hostname
    >>> mangled_dns_value("B+W 161689.00")
    'b-w-161689-00'
    >>> mangled_dns_value("C40-16671")
    'c40-16671'
    >>> mangled_dns_value("DG TEST")
    'dg-test'
    >>> mangled_dns_value("DMU50-1")
    'dmu50-1'
    >>> mangled_dns_value("Heller 58112")
    'heller-58112'
    >>> mangled_dns_value("Proj444001")
    'proj444001'
    >>> mangled_dns_value("SIM MBL65-1")
    'sim-mbl65-1'
    >>> mangled_dns_value("Simulator 1000011")
    'simulator-1000011'
    >>> mangled_dns_value("Simulator ST4")
    'simulator-st4'
    >>> mangled_dns_value("Waldrich 15091")
    'waldrich-15091'
    >>> mangled_dns_value("n/a")
    Traceback (most recent call last):
        ...
    BlacklistedError: 'n/a' is blacklisted
    >>> mangled_dns_value("00:0d:b9:3c:4a:70")
    '00-0d-b9-3c-4a-70'
    """
    mangled = str(value).lower().strip()

    if not value:
        raise ValueError("{!r} is an invalid hostname".format(value))

    if REGEX_BLACKLISTED.match(mangled):
        raise BlacklistedError("{!r} is blacklisted".format(value))

    mangled = re.sub(REGEX_INVALID_CHAR, " ", mangled)
    mangled = re.sub("\s+", "-", mangled.strip())

    return mangled


if __name__ == "__main__":
    import doctest

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # logging.basicConfig(loglevel=logging.DEBUG)
    (FAILED, SUCCEEDED) = doctest.testmod()
    print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
