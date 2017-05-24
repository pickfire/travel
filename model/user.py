from sqlalchemy import Column, Integer, String, Enum
import enum

from model import Base

class User(Base):
    __tablename__ = 'users'

    id   = Column('id', Integer, autoincrement=True, primary_key=True)
    name = Column('name', String(35))
    pasw = Column('pasw', String(35))
    role = Column(Enum(enum.Enum('role', 'employee manager finance')))

    def __repr__(self):
        return '{}: {}'.format(str(self.role)[5:], self.name)
