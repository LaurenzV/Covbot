from __future__ import annotations

from sqlalchemy import Column, Integer, String, Date, BigInteger
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import declarative_base

# declarative base class
Base = declarative_base()


class Case(Base):
    """Class representing a case entry as it is saved in the database."""
    __tablename__ = "cases"

    id: Column = Column(Integer, primary_key=True)
    date: Column = Column(Date)
    location: Column = Column(String(256))
    location_normalized: Column = Column(String(256))
    cases: Column = Column(BigInteger)
    cumulative_cases: Column = Column(BigInteger)

    def __repr__(self):
        return f"Case(id={self.id}, date={self.date}, location={self.location}, " \
               f"location_normalized={self.location_normalized}, cases={self.cases}, " \
               f"cumulative_cases={self.cumulative_cases})"


class Vaccination(Base):
    """Class representing a vaccination entry as it is saved in the database."""
    __tablename__ = "vaccinations"

    id: Column = Column(Integer, primary_key=True)
    date: Column = Column(Date)
    location: Column = Column(String(256))
    location_normalized: Column = Column(String(256))
    total_vaccinations: Column = Column(BigInteger)
    people_vaccinated: Column = Column(BigInteger)
    daily_vaccinations: Column = Column(Integer)
    daily_people_vaccinated: Column = Column(Integer)

    def __repr__(self):
        return f"Case(id={self.id}, date={self.date}, location={self.location}, " \
               f"location_normalized={self.location_normalized}, total_vaccinations={self.total_vaccinations}, " \
               f"people_vaccinated={self.people_vaccinated}, daily_vaccinations={self.daily_vaccinations}, " \
               f"daily_people_vaccinated={self.daily_people_vaccinated})"


def create_tables(engine: Engine, tables=None) -> None:
    """Creates (all) tables in the database."""
    if tables is None:
        tables = [Vaccination.__table__, Case.__table__]
    drop_tables(engine, tables)
    Base.metadata.create_all(engine, tables)


def drop_tables(engine: Engine, tables=None) -> None:
    """Drops (all) tables in the database."""
    if tables is None:
        tables = [Vaccination.__table__, Case.__table__]
    Base.metadata.drop_all(engine, tables)
