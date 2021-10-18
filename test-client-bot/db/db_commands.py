from sqlalchemy import select, delete, func
from sqlalchemy.orm import sessionmaker

from db.models import EventTable


async def db_get_item_by_id(db_session: sessionmaker, event_id: int) -> EventTable:
    """
    Return one row from database specified by ID

    @param db_session: sessionmaker

    @rtype: EventTable
    """

    sql = select(EventTable).where(EventTable.event_id == event_id)
    async with db_session() as session:
        results = await session.execute(sql)
    return results.scalars().one()


async def db_get_catalog_count(db_session: sessionmaker) -> int:
    """
    Return the number of rows in the database.

    @param db_session: sessionmaker

    @rtype: int
    """

    sql = select(func.count(EventTable.event_id))
    async with db_session() as session:
        results = await session.scalar(sql)
    return results


async def db_get_catalog_items(db_session: sessionmaker, p_limit: int, p_offset: int) -> EventTable:
    """
    Return rows from the database.

    @param db_session: sessionmaker
    @param p_limit: int
    @param p_offset: int

    @rtype: EventTable
    """

    sql = select(EventTable).order_by(EventTable.event_id.asc()).limit(p_limit).offset(p_offset)
    async with db_session() as session:
        results = await session.execute(sql)

    return results.scalars().one()


async def db_delete_item_by_id(db_session: sessionmaker, event_id: int):
    """
    Delete one row from the database specified by PK event_id.

    @param db_session: sessionmaker
    @param event_id: int
    """

    sql = delete(EventTable).where(EventTable.event_id == event_id)
    async with db_session() as session:
        await session.execute(sql)
        await session.commit()


def db_get_max_event_id(db_session: sessionmaker) -> int:
    """
    Return max(event_id) from the database.

    @param db_session: sessionmaker

    @rtype: int
    """
    qry = db_session.query(func.max(EventTable.event_id).label("event_id"))
    res = qry.one()
    max_id = int(res.event_id) if res.event_id is not None else 1
    return max_id
