from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://car_manager:123@localhost/car_management"

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(engine)
