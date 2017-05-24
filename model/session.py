from sqlalchemy import Column, Integer, String, Enum, DateTime
from datetime import datetime, timedelta
import enum
import uuid

from model import Base

class Session(Base):
    __tablename__ = 'sessions'

    id        = Column(Integer, autoincrement=True, primary_key=True)
    token     = Column('token', String(32))
    userid    = Column('uid', Integer)
    createAt  = Column(DateTime)
    expiresAt = Column(DateTime)

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.token     = uuid.uuid4().hex
        self.createAt  = datetime.now()
        self.expiresAt = datetime.now() + timedelta(hours=1)
