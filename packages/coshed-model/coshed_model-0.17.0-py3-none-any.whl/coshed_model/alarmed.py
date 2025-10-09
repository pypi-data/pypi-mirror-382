#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import zlib

import pendulum

PATTERN_ALARM_CODE = r"^((?P<code>[a-z0-9]\s?[a-z0-9]+)|(?P<crap_code>.*?) \| (?P<text>.*?))\s*$"
REGEX_ALARM_CODE = re.compile(PATTERN_ALARM_CODE, re.I)


class Alarmed(dict):
    """
    Alarm event model

    Attributes:
        dt_begin (pendulum.Datetime): begin
        dt_end (pendulum.Datetime): end
        code (str): Error code
        message (str): Error message
        alarm_id (str): Alarm ID

    >>> al = Alarmed()
    Traceback (most recent call last):
        ...
    ValueError: Empty Code
    >>> allen = Alarmed(code="x")
    Traceback (most recent call last):
        ...
    ValueError: No Begin
    """

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        for r_key in ("dt_begin", "dt_end", "code", "message"):
            try:
                self[r_key]
            except KeyError:
                self[r_key] = None

        if self.get("dt") and {self.get("dt_begin"), self.get("dt_end")} == {
            None
        }:
            value = self["dt"]
            self["dt_begin"] = value
            self["dt_end"] = value
            del self["dt"]

        for dt_key in ("dt_begin", "dt_end"):
            if isinstance(self[dt_key], str):
                self[dt_key] = pendulum.parse(self[dt_key])

        if self.get("text") and self.get("message") is None:
            self["message"] = self["text"]
            del self["text"]

        self["alarm_id"] = self._mk_alarm_id()

        if self.dt_begin is None:
            raise ValueError("No Begin")

    @classmethod
    def mk_alarm_id(cls, code, message):
        """
        Generate an alarm ID for an alarm log item containing an alarm code and
        some descriptive text.

        If the text is empty the Alarm ID equals the alarm code.

        Alarm ID consist of the Alarm Code and an hex encoded CRC32 hash of the
        text concatenated by a dot.

        .. warning::

            It is assumed that the text is encoded in valid ``UTF-8``!

        Text normalisation:

            #. Leading and trailing whitespaces are removed
            #. String is converted to lowercase

        Args:
            code (str): Alarm code
            message (str): Alarm text

        Returns:
            str: Alarm ID

        >>> Alarmed.mk_alarm_id('710531', "710531 | HYDRAULIK: Bitte Öl auffüllen")
        '710531.5CB5A110'
        >>> Alarmed.mk_alarm_id('700244', '700244 | BAR FEEDER: Axes and spindles of machine blocked')
        '700244.B8D47740'
        >>> Alarmed.mk_alarm_id('27097', '27097 | NCU_1: SPL-Start nicht erfolgt')
        '27097.D020A11'

        """
        if not code:
            code = ""

        if not code:
            raise ValueError("Empty Code")

        if not message:
            return code

        mangled = message.strip().lower()
        crc = "{:X}".format(zlib.crc32(mangled.encode("utf-8")))

        return f"{code}.{crc}"

    @classmethod
    def alarm_id_from_string(cls, value):
        """
        Generate an alarm ID by interpreting given value

        Args:
            value (str): input value

        Returns:
            str: alarm ID

        >>> Alarmed.alarm_id_from_string("710531 | HYDRAULIK: Bitte Öl auffüllen")
        '710531.5CB5A110'
        >>> Alarmed.alarm_id_from_string('700244 | BAR FEEDER: Axes and spindles of machine blocked')
        '700244.B8D47740'
        >>> Alarmed.alarm_id_from_string('27097 | NCU_1: SPL-Start nicht erfolgt')
        '27097.D020A11'
        >>> Alarmed.alarm_id_from_string('27097')
        '27097'
        """
        matcher = REGEX_ALARM_CODE.match(value)

        if matcher:
            gdict = matcher.groupdict()

            if gdict.get("crap_code"):
                return Alarmed.mk_alarm_id(
                    code=gdict.get("crap_code"), message=value
                )
            return Alarmed.mk_alarm_id(gdict.get("code"), "")

        return value

    def _mk_alarm_id(self):
        return Alarmed.mk_alarm_id(self.get("code"), self.get("message"))

    def __str__(self):
        period = self.dt_begin.diff(self.dt_end)

        return "<Alarm> {code:>12} @{dt_begin} {ts:16.1f}s: {message}".format(
            dt_begin=self.dt_begin.format("YYYY-MM-DD HH:mm:ss.S"),
            code=self.code,
            message=self.message,
            ts=period.total_seconds(),
        )

    @property
    def repeater_v2_record(self):
        """
        Get alarm data as a list to be used for repeater V2 endpoint.

        Returns:
            list: Alarm Repeater V2 record

        >>> alf = Alarmed(dt="2021-01-01T17:03:00Z", code="red", message="UH-OH!")
        >>> alf.repeater_v2_record
        ['2021-01-01T17:03:00+00:00', 'red.B3F10B52']
        >>> ale = Alarmed(dt="2021-01-01T17:03:00Z", code="red")
        >>> ale.repeater_v2_record
        ['2021-01-01T17:03:00+00:00', 'red']
        """
        return [self.dt_begin.to_rfc3339_string(), self.alarm_id]

    @property
    def dt_begin(self):
        return self["dt_begin"]

    @property
    def dt_end(self):
        return self["dt_end"]

    @property
    def code(self):
        return self["code"]

    @property
    def alarm_id(self):
        return self["alarm_id"]

    @property
    def message(self):
        return self["message"]


if __name__ == "__main__":
    import doctest

    (FAILED, SUCCEEDED) = doctest.testmod()
    print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
