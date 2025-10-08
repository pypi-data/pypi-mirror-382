# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

import logging
from datetime import datetime
from typing import Optional, Tuple, Iterable, Sequence, List, Union

# -------------------
# Third party imports
# -------------------

from pubsub import pub


# from typing_extensions import Self
from sqlalchemy import select, and_
from tessdbdao import (
    TimestampSource,
    ReadingSource,
    ValidState,
)

from tessdbdao.asyncio import Units, NameMapping, Tess, Tess4cReadings, TessReadings

# --------------
# local imports
# -------------

from ...util import Session, async_lru_cache
from ...model import (
    ReferencesInfo,
    ReadingInfo1c,
    ReadingInfo4c,
    ReadingInfo,
    ReadingEvent,
    LogSpace,
    IMPOSSIBLE_SIGNAL_STRENGTH,
    IMPOSSIBLE_TEMPERATURE,
)

# ----------------
# Global variables
# ----------------

PhotReadings = Union[TessReadings, Tess4cReadings]

log = logging.getLogger(LogSpace.DBASE)

# ===================================
# Registry process auxiliar functions
# ===================================


def split_datetime(tstamp: datetime) -> Tuple[int, int]:
    """Round a timestamp to the nearest minute"""
    date_id = tstamp.year * 10000 + tstamp.month * 100 + tstamp.day
    time_id = tstamp.hour * 10000 + tstamp.minute * 100 + tstamp.second
    return date_id, time_id


# ------------------
# Auxiliar functions
# ------------------


class HashMismatchError(RuntimeError):
    """photometer hash mismatch error"""

    pass


@async_lru_cache(maxsize=10)
async def resolve_units_id(
    session: Session, source: ReadingSource, tstamp_src: TimestampSource
) -> int:
    """For readings recovery/batch uploads"""
    query = select(Units.units_id).where(
        Units.timestamp_source == tstamp_src,
        Units.reading_source == source,
    )
    return (await session.scalars(query)).one()


async def find_photometer_by_name(
    session: Session, name: str, mac_hash: str, tstamp: datetime, latest: bool
) -> Optional[Tess]:
    if latest:
        query = (
            select(Tess)
            .join(
                NameMapping,
                NameMapping.mac_address == Tess.mac_address,
            )
            .where(
                NameMapping.name == name,
                NameMapping.valid_state == ValidState.CURRENT,
                and_(Tess.valid_since <= tstamp, tstamp <= Tess.valid_until),
            )
            .order_by(Tess.valid_since.desc())
        )
    else:
        query = (
            select(Tess)
            .join(
                NameMapping,
                NameMapping.mac_address == Tess.mac_address,
            )
            .where(
                NameMapping.name == name,
                and_(NameMapping.valid_since <= tstamp, tstamp <= NameMapping.valid_until),
                and_(Tess.valid_since <= tstamp, tstamp <= Tess.valid_until),
            )
            .order_by(Tess.valid_since.desc())
        )

    result = (await session.scalars(query)).all()
    result = result[0] if result else None  # Choose the most recent one
    if result and mac_hash and mac_hash != "".join(result.mac_address.split(":"))[-3:]:
        raise HashMismatchError(mac_hash, result.mac_address)
    return result


async def resolve_references(
    session: Session,
    reading: ReadingInfo,
    auth_filter: bool,
    latest: bool,
    source: ReadingSource,
) -> Optional[ReferencesInfo]:
    plog = logging.getLogger(reading.name)
    pub.sendMessage(ReadingEvent.WRITE_REQUEST, source=source)
    units_id = await resolve_units_id(session, source, reading.tstamp_src)
    try:
        phot = await find_photometer_by_name(
            session, reading.name, reading.hash, reading.tstamp, latest
        )
        if phot is None:
            pub.sendMessage(ReadingEvent.NOT_REGISTERED, source=source)
            log.info(
                "No TESS %s registered ! => %s",
                reading.name,
                dict(reading),
            )
            plog.debug(
                "No TESS %s registered ! => %s",
                reading.name,
                dict(reading),
            )
            return None
    except HashMismatchError as e:
        pub.sendMessage(ReadingEvent.HASH_MISMATCH, source=source)
        log.info(
            "[%s] Reading rejected by hash mismatch: %s => %s", reading.name, str(e), dict(reading)
        )
        plog.debug(
            "[%s] Reading rejected by hash mismatch: %s => %s", reading.name, str(e), dict(reading)
        )
        return None
    else:
        if auth_filter and not phot.authorised:
            pub.sendMessage(ReadingEvent.NOT_AUTHORISED, source=source)
            log.info("[%s]: Not authorised: %s", reading.name, dict(reading))
            plog.debug("[%s]: Not authorised: %s", reading.name, dict(reading))
            return None
        date_id, time_id = split_datetime(reading.tstamp)
        return ReferencesInfo(
            date_id=date_id,
            time_id=time_id,
            tess_id=phot.tess_id,
            location_id=phot.location_id,
            observer_id=phot.observer_id,
            units_id=units_id,
        )


async def resolve_references_seq(
    session: Session,
    readings: Sequence[ReadingInfo],
    auth_filter: bool,
    latest: bool,
    source: ReadingSource,
) -> List[Optional[ReferencesInfo]]:
    return [
        await resolve_references(session, reading, auth_filter, latest, source)
        for reading in readings
    ]


def tess_new(
    reading: ReadingInfo1c,
    reference: ReferencesInfo,
) -> Tess:
    return TessReadings(
        date_id=reference.date_id,
        time_id=reference.time_id,
        tess_id=reference.tess_id,
        location_id=reference.location_id,
        observer_id=reference.observer_id,
        units_id=reference.units_id,
        sequence_number=reading.sequence_number,
        frequency=reading.freq1,
        magnitude=reading.mag1,
        box_temperature=reading.box_temperature,
        sky_temperature=reading.sky_temperature,
        azimuth=reading.azimuth,
        altitude=reading.altitude,
        longitude=reading.longitude,
        latitude=reading.latitude,
        elevation=reading.elevation,
        signal_strength=reading.signal_strength,
        hash=reading.hash,
    )


def tess4c_new(
    reading: ReadingInfo4c,
    reference: ReferencesInfo,
) -> None:
    return Tess4cReadings(
        date_id=reference.date_id,
        time_id=reference.time_id,
        tess_id=reference.tess_id,
        location_id=reference.location_id,
        observer_id=reference.observer_id,
        units_id=reference.units_id,
        sequence_number=reading.sequence_number,
        freq1=reading.freq1,
        mag1=reading.freq1,
        freq2=reading.freq2,
        mag2=reading.mag2,
        freq3=reading.freq3,
        mag3=reading.mag3,
        freq4=reading.freq4,
        mag4=reading.mag4,
        # Early TESS4C modes doid not provide this
        box_temperature=reading.box_temperature
        if reading.box_temperature is not None
        else IMPOSSIBLE_TEMPERATURE,
        sky_temperature=reading.sky_temperature
        if reading.sky_temperature is not None
        else IMPOSSIBLE_TEMPERATURE,
        azimuth=reading.azimuth,
        altitude=reading.altitude,
        longitude=reading.longitude,
        latitude=reading.latitude,
        elevation=reading.elevation,
        # Early TESS4C modes doid not provide this
        signal_strength=reading.signal_strength
        if reading.signal_strength is not None
        else IMPOSSIBLE_SIGNAL_STRENGTH,
        hash=reading.hash,
    )


def new_dbobject(reading: ReadingInfo, reference: ReferencesInfo) -> PhotReadings:
    if isinstance(reading, ReadingInfo4c):
        return tess4c_new(reading, reference)
    else:
        return tess_new(reading, reference)


async def _photometer_looped_write(
    session: Session,
    dbobjs: Iterable[PhotReadings],
    items: Sequence[Tuple[ReadingInfo1c, ReferencesInfo]],
    source: ReadingSource,
):
    """One by one commit of database records"""
    for i, dbobj in enumerate(dbobjs):
        async with session.begin():
            session.add(dbobj)
            try:
                await session.commit()
            except Exception:
                pub.sendMessage(ReadingEvent.SQL_ERROR, source=source)
                log.warning("Discarding reading by SQL Integrity error: %s", dict(items[i][0]))
                await session.rollback()
            else:
                pub.sendMessage(ReadingEvent.SQL_OK, source=source, count=1)


# ==================
# READING PROCESSING
# ==================


async def photometer_batch_write(
    session: Session,
    readings: Iterable[ReadingInfo],
    auth_filter: bool = False,
    latest: bool = True,
    source: ReadingSource = ReadingSource.DIRECT,
    dry_run: bool = False,
) -> None:
    await session.begin()
    references = await resolve_references_seq(
        session,
        readings,
        auth_filter,
        latest,
        source,
    )
    items = tuple(filter(lambda x: x[1] is not None, zip(readings, references)))
    objs = tuple(new_dbobject(reading, reference) for reading, reference in items)
    session.add_all(objs)
    if dry_run:
        log.warning("Dry run mode. Database not written")
        await session.rollback()
    else:
        try:
            await session.commit()
        except Exception as e:
            log.error(str(e).split("\n")[0])
            log.info("Looping %d readings one by one.", len(objs))
            await session.rollback()
            await session.close()
            await _photometer_looped_write(session, objs, items, source)
        else:
            pub.sendMessage(ReadingEvent.SQL_OK, source=source, count=len(objs))
            await session.close()


async def photometer_resolved_batch_write(
    session: Session,
    items: Sequence[Tuple[ReadingInfo, ReferencesInfo]],
    source: ReadingSource = ReadingSource.DIRECT,
    dry_run: bool = False,
) -> None:
    await session.begin()
    objs = tuple(new_dbobject(reading, reference) for reading, reference in items)
    session.add_all(objs)
    if dry_run:
        log.warning("Dry run mode. Database not written")
        await session.rollback()
    else:
        try:
            await session.commit()
        except Exception as e:
            log.error(str(e).split("\n")[0])
            log.info("Looping %d readings one by one.", len(objs))
            await session.rollback()
            await session.close()
            await _photometer_looped_write(session, objs, items, source)
        else:
            pub.sendMessage(ReadingEvent.SQL_OK, source=source, count=len(objs))
            await session.close()
