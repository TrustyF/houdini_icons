import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


db_username = os.getenv('MYSQL_DATABASE_USERNAME')
db_password = os.getenv('MYSQL_DATABASE_PASSWORD')
db_name = 'TrustyFox$houdini_icons'

local_database_uri = f'mysql+pymysql://root:{db_password}@127.0.0.1:3306/{db_name}'
local_sqlite_uri = "sqlite:///assets/icon_db.db"

engine = create_engine(local_sqlite_uri)
Session_maker = sessionmaker(bind=engine)
session = Session_maker()
Base = declarative_base()

from icon_model import *
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)