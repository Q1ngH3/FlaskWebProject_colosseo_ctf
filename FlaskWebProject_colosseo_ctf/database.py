from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqlconnector://myctf:myctf@127.0.0.1:3306/myctf?charset=utf8',echo = True,encoding='utf-8',convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from FlaskWebProject_colosseo_ctf import models
    Base.metadata.create_all(bind=engine)