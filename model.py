from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

car_garage = Table(
    'car_garage',
    Base.metadata,
    Column('carId', Integer, ForeignKey('car.id', ondelete='CASCADE'), primary_key=True),
    Column('garageId', Integer, ForeignKey('garage.id', ondelete='CASCADE'), primary_key=True)
)

class Garage(Base):
    __tablename__ = 'garage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    capacity = Column(Integer, nullable=False)
    cars = relationship('Car', secondary=car_garage, back_populates='garages')
    maintenances = relationship('Maintenance', back_populates='garage')

class Car(Base):
    __tablename__ = 'car'
    id = Column(Integer, primary_key=True, autoincrement=True)
    make = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    productionYear = Column(Integer, nullable=False)
    licensePlate = Column(String(20), nullable=False, unique=True)
    garages = relationship('Garage', secondary=car_garage, back_populates='cars')
    maintenances = relationship('Maintenance', back_populates='car')

class Maintenance(Base):
    __tablename__ = 'maintenance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    serviceType = Column(String(255), nullable=False)
    scheduledDate = Column(Date, nullable=True)
    carId = Column(Integer, ForeignKey('car.id', ondelete='SET NULL'), nullable=True)
    garageId = Column(Integer, ForeignKey('garage.id', ondelete='SET NULL'), nullable=True)
    car = relationship('Car', back_populates='maintenances')
    garage = relationship('Garage', back_populates='maintenances')
