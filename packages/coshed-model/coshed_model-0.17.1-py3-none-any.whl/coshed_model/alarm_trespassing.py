#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. seealso::

    * https://www.sqlitetutorial.net/sqlite-trigger/
    * https://www.sqlitetutorial.net/sqlite-replace-statement/
    * https://www.sqlitetutorial.net/sqlite-functions/sqlite-coalesce/
    * https://www.sqlite.org/inmemorydb.html
    * https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#connect-strings
    * https://docs.sqlalchemy.org/en/14/core/compiler.html#utc-timestamp-function
    * https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    * https://sqlite.org/lang_datefunc.html

Tables
------

.. code-block:: sql
   :linenos:

    CREATE TABLE alarm_log (
        id INTEGER NOT NULL,
        alarm_id TEXT NOT NULL,
        threshold INTEGER DEFAULT 3,
        threshold_seconds INTEGER DEFAULT 0,
        shot INTEGER DEFAULT '0',
        occurrence DATETIME DEFAULT (CURRENT_TIMESTAMP),
        PRIMARY KEY (id)
    );

.. code-block:: sql
   :linenos:

    CREATE TABLE alarms (
        id text PRIMARY KEY,
        threshold INTEGER DEFAULT 3,
        count INTEGER DEFAULT 0,
        occurrence DATE DEFAULT CURRENT_TIMESTAMP
    );

.. code-block:: sql
   :linenos:

    CREATE TABLE trespass (
        id INTEGER PRIMARY KEY,
        alarm_id TEXT,
        threshold INTEGER,
        occurrence DATE,
        discovery DATE DEFAULT CURRENT_TIMESTAMP
    );

.. code-block:: sql
   :linenos:

    CREATE TABLE trespass_database_information (
        id INTEGER NOT NULL, 
        key TEXT NOT NULL, 
        value TEXT NOT NULL, 
        dt DATETIME DEFAULT (CURRENT_TIMESTAMP), 
        PRIMARY KEY (id)
    )

Triggers
--------

.. code-block:: sql
   :linenos:

    CREATE TRIGGER trespass_insert
    AFTER INSERT ON alarms
    WHEN
        new.count >= new.threshold
    BEGIN
        INSERT INTO trespass (alarm_id, threshold, occurrence) VALUES(new.id, new.threshold, new.occurrence);
        UPDATE alarms SET count=0 WHERE id=new.id;
        UPDATE alarm_log SET shot=1 WHERE alarm_id=new.id;
    END;

.. code-block:: sql
   :linenos:

    CREATE TRIGGER drop_outdated
    AFTER INSERT ON alarm_log
    BEGIN
        DELETE FROM alarm_log WHERE alarm_id = new.alarm_id AND id != new.id AND new.threshold_seconds > 0 AND strftime("%s", occurrence) + new.threshold_seconds - strftime("%s", new.occurrence) < 0;
        DELETE FROM alarm_log WHERE alarm_id = new.alarm_id AND id != new.id AND occurrence=new.occurrence;

        INSERT OR REPLACE INTO alarms (id, count, threshold, occurrence) VALUES(new.alarm_id, (SELECT COUNT(*) FROM alarm_log WHERE alarm_id=new.alarm_id AND shot=0), new.threshold, new.occurrence);
    END;

Example insert
--------------

.. code-block:: sql
   :linenos:

    INSERT
    INTO alarm_log (alarm_id, occurrence, threshold, threshold_seconds) 
    VALUES("1", "2021-01-01T00:00:00Z", 3, 3600);

"""
import datetime

import pendulum
from sqlalchemy import event, DDL
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import types
from sqlalchemy.sql import text

Base = declarative_base()


# https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
# https://docs.sqlalchemy.org/en/14/core/compiler.html#utc-timestamp-function
class utcnow(expression.FunctionElement):
    type = DateTime()


# https://docs.sqlalchemy.org/en/14/core/compiler.html#utc-timestamp-function
@compiles(utcnow, "sqlite")
def sqlite_utcnow(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"


class DateTimeUTC(types.TypeDecorator):
    impl = types.DateTime
    LOCAL_TIMEZONE = datetime.datetime.utcnow().astimezone().tzinfo

    def process_bind_param(self, value: datetime.datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(pendulum.UTC)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=pendulum.UTC)

        return value.astimezone(pendulum.UTC)


#: default value - threshold number
DEFAULT_THRESHOLD = 3

#: default value - timeframe threshold
DEFAULT_THRESHOLD_SECONDS = 0

#: database schema version indicator
DATABASE_SCHEMA_VERSION = 2


class AlarmLog(Base):
    """
    Alarm events.

    Attributes:
        id (str): Alarm Identifier
        threshold (int): Threshold number for counting as trespassing
        threshold_seconds (int): timeframe threshold for counting as trespassing
        occurrence(datetime.datetime): occurrence datetime
        shot(int): Indicator if entry has already been considered

    """

    __tablename__ = "alarm_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_id = Column(Text, nullable=False)
    threshold = Column(Integer, server_default=str(DEFAULT_THRESHOLD))
    threshold_seconds = Column(
        Integer, server_default=str(DEFAULT_THRESHOLD_SECONDS)
    )
    shot = Column(Integer, server_default="0")
    occurrence = Column(DateTimeUTC, server_default=utcnow())

    def __init__(
        self, alarm_id, occurrence=None, threshold=None, threshold_seconds=None
    ):
        self.alarm_id = alarm_id

        if threshold is not None:
            self.threshold = threshold

        if threshold_seconds is not None:
            self.threshold_seconds = threshold_seconds

        if occurrence is not None:
            self.occurrence = occurrence

    def __str__(self) -> str:
        return "<{klass} {alarm_id!r} {occurrence!s}>".format(
            klass=self.__class__.__name__,
            alarm_id=self.alarm_id,
            occurrence=self.occurrence,
        )


class Alarm(Base):
    """
    Alarm counter.

    Attributes:
        id (str): Alarm Identifier
        threshold (int): Threshold number for counting as trespassing
        count (int): occurrences count
        occurrence(datetime.datetime): most recent occurrence datetime

    """

    __tablename__ = "alarms"

    id = Column(Text, primary_key=True)
    threshold = Column(Integer, server_default=str(DEFAULT_THRESHOLD))
    count = Column(Integer, server_default="0")
    occurrence = Column(DateTimeUTC, server_default=utcnow())

    def __init__(self, id, threshold=None, count=None, occurrence=None):
        self.id = id

        if threshold is not None:
            self.threshold = threshold

        if not count:
            count = 1
        self.count = count

        if occurrence is not None:
            self.occurrence = occurrence


class Trespass(Base):
    """
    Trespassing events.

    Attributes:
        id (str): Row ID
        threshold (int): Threshold number for counting as trespassing
        threshold_seconds (int): timeframe threshold for counting as trespassing
        occurrence (datetime.datetime): most recent occurrence datetime
        discovery (datetime.datetime): datetime of trespassing discovery

    """

    __tablename__ = "trespass"

    id = Column(Integer, primary_key=True)
    alarm_id = Column(Text, nullable=False)
    threshold = Column(Integer)
    threshold_seconds = Column(Integer)
    occurrence = Column(DateTimeUTC)
    discovery = Column(DateTimeUTC, server_default=utcnow())

    def __init__(self, alarm_id):
        self.alarm_id = alarm_id

    def __str__(self) -> str:
        return "<{klass} {alarm_id!r} {occurrence!s}>".format(
            klass=self.__class__.__name__,
            alarm_id=self.alarm_id,
            occurrence=self.occurrence,
        )

    @property
    def json(self):
        dt_occurrence = pendulum.instance(self.occurrence).in_tz(pendulum.UTC)
        dt_discovery = pendulum.instance(self.discovery).in_tz(pendulum.UTC)

        return dict(
            occurrence=dt_occurrence.to_rfc3339_string(),
            discovery=dt_discovery.to_rfc3339_string(),
            alarm_id=self.alarm_id,
        )


class TresspassDatabaseInformation(Base):
    """
    (Internal) Database key/value pairs for storing meta data.

    Attributes:
        id (str): Row ID
        key (str): key
        value (str): value

    """

    __tablename__ = "trespass_database_information"

    id = Column(Integer, primary_key=True)
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    dt = Column(DateTimeUTC, server_default=utcnow())

    def __init__(self, key, value):
        self.key = key
        self.value = value


event.listen(
    Trespass.__table__,
    "after_create",
    DDL(
        """CREATE TRIGGER trespass_insert
        AFTER INSERT ON alarms
        WHEN 
                new.count >= new.threshold
        BEGIN
            INSERT INTO trespass (alarm_id, threshold, occurrence) VALUES(new.id, new.threshold, new.occurrence);
            UPDATE alarms SET count=0 WHERE id=new.id;
            UPDATE alarm_log SET shot=1 WHERE alarm_id=new.id;
        END;
        """
    ),
)

event.listen(
    AlarmLog.__table__,
    "after_create",
    DDL(
        """CREATE TRIGGER drop_outdated
        AFTER INSERT ON alarm_log
        BEGIN
            DELETE FROM alarm_log WHERE alarm_id = new.alarm_id AND id != new.id AND new.threshold_seconds > 0 AND strftime("%%s", occurrence) + new.threshold_seconds - strftime("%%s", new.occurrence) < 0;
            DELETE FROM alarm_log WHERE alarm_id = new.alarm_id AND id != new.id AND occurrence=new.occurrence;

            INSERT OR REPLACE INTO alarms (id, count, threshold, occurrence) VALUES(new.alarm_id, (SELECT COUNT(*) FROM alarm_log WHERE alarm_id=new.alarm_id AND shot=0), new.threshold, new.occurrence);
        END;
        """
    ),
)

event.listen(
    TresspassDatabaseInformation.__table__,
    "after_create",
    DDL(
        "INSERT INTO trespass_database_information (key, value) VALUES('schema_version', '{!s}');".format(
            DATABASE_SCHEMA_VERSION
        )
    ),
)

event.listen(
    TresspassDatabaseInformation.__table__,
    "after_create",
    DDL(
        "INSERT INTO trespass_database_information (key, value) VALUES('created', '{!s}');".format(
            pendulum.now(pendulum.UTC).to_datetime_string()
        )
    ),
)


def add_alarm_occurrence(session, alarm_id, occurrence=None):
    stmt_args = dict(id=alarm_id)

    if occurrence:
        statement = text(
            """
            INSERT INTO alarm_log (alarm_id, occurrence)
            VALUES (
                :id,
                :occurrence
            )
        """
        )
        x = pendulum.instance(occurrence)
        stmt_args["occurrence"] = x.in_tz(pendulum.UTC).to_datetime_string()
    else:
        statement = text(
            """
            INSERT INTO alarm_log (alarm_id)
            VALUES (
                :id
            )
        """
        )
    session.execute(statement, stmt_args)
    session.commit()
