#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def cfapp_base_url(value, env_name=None, **kwargs):
    """

    >>> cfapp_base_url("crap")
    'https://crap.cfapps.eu10.hana.ondemand.com'
    >>> cfapp_base_url("crap", env_name="prod")
    'https://crap.cfapps.eu10.hana.ondemand.com'
    >>> cfapp_base_url("crap", env_name="dev")
    'https://crap-dev.cfapps.eu10.hana.ondemand.com'
    >>> cfapp_base_url("crap", env_name="dev", prefixed=True)
    'https://dev-crap.cfapps.eu10.hana.ondemand.com'
    """
    CONTAINER_APP_ENV_DNS_SUFFIX = os.environ.get(
        "CONTAINER_APP_ENV_DNS_SUFFIX"
    )

    if CONTAINER_APP_ENV_DNS_SUFFIX:
        ENV_NAME = os.environ.get("ENV_NAME")
        scheme = kwargs.get("scheme", "https")
        hostname = value
        domain = CONTAINER_APP_ENV_DNS_SUFFIX

        if env_name is None or env_name != ENV_NAME:
            env_key = f"ENV_DOMAIN_{str(env_name).upper()}"

            try:
                domain = os.environ[env_key]
            except KeyError:
                pass

        fqdn = f"{hostname}.{domain}"

        if kwargs.get("want_fqdn", True):
            return f"{scheme}://{fqdn}"

        return f"{scheme}://{hostname}"

    return "https://{hostname}.cfapps.eu10.hana.ondemand.com".format(
        hostname=environment_specific_name(value, env_name=env_name, **kwargs)
    )


def environment_specific_name(value, env_name=None, **kwargs):
    """
    Generate an environment specific name for ``value``.

    Schema for determining the environment specific name is

    **Append environment name separated by a dash if environment name is not** ``prod``

    .. note::

        This function is case agnostic, returned values are lower case.

    Args:
        value: value
        env_name (str, optional): environment name

    Keyword Args:
        prefixed (bool): Force prefix mode (even if it is ``prod``)

    Returns:
        str: environment specific name

    >>> environment_specific_name(0)
    Traceback (most recent call last):
        ...
    AttributeError: 'int' object has no attribute 'lower'
    >>> environment_specific_name(None)
    Traceback (most recent call last):
        ...
    AttributeError: 'NoneType' object has no attribute 'lower'
    >>> environment_specific_name("x")
    'x'
    >>> environment_specific_name("X")
    'x'
    >>> environment_specific_name("x", env_name="prod")
    'x'
    >>> environment_specific_name("x", env_name="PROD")
    'x'
    >>> environment_specific_name("x", env_name="prod", prefixed=True)
    'prod-x'
    >>> environment_specific_name("x", env_name="PROD", prefixed=True)
    'prod-x'
    >>> environment_specific_name("x", env_name="qa")
    'x-qa'
    >>> environment_specific_name("x", env_name="dev")
    'x-dev'
    """
    if env_name is None:
        return value.lower()

    if kwargs.get("prefixed"):
        return "-".join((env_name, value)).lower()

    if env_name.lower() != "prod":
        return "-".join((value, env_name)).lower()

    return value.lower()


if __name__ == "__main__":
    import doctest

    (FAILED, SUCCEEDED) = doctest.testmod()
    print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
