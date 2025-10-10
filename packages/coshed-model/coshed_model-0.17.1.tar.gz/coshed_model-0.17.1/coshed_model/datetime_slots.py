#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pendulum


class TimestampSlotEmptyError(ValueError):
    """
    Exception to be raised when a timestamp slot is empy
    """

    pass


class InvalidSlotError(ValueError):
    """
    Exception to be raised when one tries to add a value for a non-existing/invalid slot
    """

    pass


class TimestampSlot(set):
    """
    Model class for holding unique timestamp values.
    """

    def __init__(self, *args, **kwargs):
        self.limit = kwargs.get("limit", 0)
        if len(args) == 1:
            for item in iter(args[0]):
                self |= item

    @classmethod
    def int_timestamp(cls, in_value):
        """
        Convert ``in_value`` to an integer timestamp

        Args:
            in_value (any): input value, either ``int``, a \
                :py:class:`datetime.datetime` object or a string \
                representation of a datetime that is parseable by \
                pendulum library

        Returns:
            int: timestamp value
        """
        if isinstance(in_value, pendulum.DateTime):
            val = in_value.in_tz(pendulum.UTC).int_timestamp
        elif isinstance(in_value, int):
            val = (
                pendulum.from_timestamp(in_value)
                .in_tz(pendulum.UTC)
                .int_timestamp
            )
        else:
            dt = pendulum.parse(in_value)
            val = dt.in_tz(pendulum.UTC).int_timestamp

        return val

    def __ior__(self, other):
        return super().__ior__(set([TimestampSlot.int_timestamp(other)]))

    def __iadd__(self, other):
        return NotImplemented

    def __isub__(self, other):
        return NotImplemented

    def dt_objects(self, in_period=None):
        """
        Generator for converting values to datetime objects.
        Optionally filtered by a period object defining the
        boundaries within the yielded values need to be in.

        Args:
            in_period (pendulum.Period, optional): Datetime period. Defaults to None.

        Yields:
            datetime.datetime: datetime object
        """
        for value in self:
            dt_obj = pendulum.from_timestamp(value)

            try:
                if dt_obj in in_period:
                    yield dt_obj
            except TypeError:
                yield dt_obj

    def remove_items_in_period(self, in_period):
        """
        Remove values contained in given period from current
        object.

        Args:
            in_period (pendulum.Period): Datetime period
        """
        for value in list(self):
            if pendulum.from_timestamp(value) in in_period:
                self.remove(value)

    def json(self, **kwargs):
        """
        Generate a list of timestamp values suitable to be encoded as JSON data.
        The list is sorted in such ways
        that the first value will be the maximum value.
        Optionally the amount of returned values is limited by :py:data:`~.limit`
        or ``limit`` keyword argument.


        Raises:
            TimestampSlotEmptyError: If no values are available

        Returns:
            list: sorted list of unique timestamp values
        """
        limit = self.limit
        r_sorted = list(reversed(sorted(self)))

        if len(r_sorted) == 0:
            raise TimestampSlotEmptyError()

        if kwargs.get("limit"):
            limit = kwargs.get("limit")

        if limit:
            r_sorted = r_sorted[:limit]

        return r_sorted


class SlotsDocument(object):
    def __init__(self, policy_data=None) -> None:
        self._slot_policy = dict()
        self._data = dict()

        if policy_data is not None:
            for key, value in policy_data.items():
                self._slot_policy[key] = value

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    @property
    def data(self):
        return self._data

    def keys(self):
        return self._data.keys()

    def load(self, data):
        """
        Load slot values by evaluating ``data`` key/value pairs.

        Args:
            data (dict): slot values
        """
        for key, value in data.items():
            if key not in self._slot_policy:
                continue

            self._data[key] = TimestampSlot(
                value, limit=self._slot_policy[key]
            )

    def add(self, key, value):
        """
        Add timestamp value for ``key``.

        Args:
            key (str): data key
            value (any): timestamp value

        Raises:
            InvalidSlotError: If data for an invalid/unknown slot were to be added
        """
        if key not in self._slot_policy:
            raise InvalidSlotError(key)

        try:
            self._data[key] |= value
        except KeyError:
            self._data[key] = TimestampSlot([value])

    def json(self):
        """
        Generate a representation of the slots contained suitable to be encoded
        as JSON data.

        Returns:
            dict: slot data document
        """
        document = dict(data=dict())

        for key, value in self._data.items():
            try:
                document["data"][key] = value.json()
            except TimestampSlotEmptyError:
                pass

        document["dt"] = pendulum.now(pendulum.UTC).to_rfc3339_string()

        return document
