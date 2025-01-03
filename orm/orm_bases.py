from datetime import datetime
from fastapi.exceptions import HTTPException
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapped_column, Mapped, Session

Base = declarative_base()


class CarGarageAssociations(Base):
    """Association table for many-to-many relationship between cars and garages"""
    __tablename__ = "car_garage"
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.car_id"), primary_key=True)
    garage_id: Mapped[int] = mapped_column(ForeignKey("garages.garage_id"),
                                           primary_key=True)


class Garages(Base):
    __tablename__ = "garages"

    garage_id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                           autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    cars = relationship(
        "Cars",
        secondary="car_garage",
        back_populates="garages",
        foreign_keys="[CarGarageAssociations.car_id, CarGarageAssociations.garage_id]"
    )
    maintenances = relationship("Maintenances", back_populates="garage")


class Cars(Base):
    __tablename__ = "cars"

    car_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    production_year: Mapped[int] = mapped_column(Integer, nullable=False)
    license_plate: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    garages = relationship(
        "Garages",
        secondary="car_garage",
        back_populates="cars",
        foreign_keys="[CarGarageAssociations.car_id, CarGarageAssociations.garage_id]"
    )
    maintenances = relationship("Maintenances", back_populates="car")


class Maintenances(Base):
    __tablename__ = "maintenances"

    maintenance_id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                                autoincrement=True)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.car_id"),
                                        nullable=False)
    garage_id: Mapped[int] = mapped_column(Integer, ForeignKey("garages.garage_id"),
                                           nullable=False)
    service_type: Mapped[str] = mapped_column(String, nullable=False)
    scheduled_date: Mapped[str] = mapped_column(Date, nullable=False)

    car = relationship("Cars", back_populates="maintenances")
    garage = relationship("Garages", back_populates="maintenances")
