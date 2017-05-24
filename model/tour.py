from sqlalchemy import Column, Integer, String, Enum, Date
import enum

from model import Base

class Tour(Base):
    __tablename__ = 'tours'

    id    = Column(Integer, autoincrement=True, primary_key=True)
    name  = Column(String(35))
    desc  = Column(String(200), default='')
    state = Column(Enum(enum.Enum('state', 'draft submitted approved rejected request')), default='draft')

    start = Column(Date)
    end   = Column(Date)
    mode  = Column(Enum(enum.Enum('travelmode', 'plane train')))

    ticket_cost   = Column(Integer, nullable=True)
    cab_home_cost = Column(Integer, nullable=True)
    cab_dest_cost = Column(Integer, nullable=True)
    hotel_cost    = Column(Integer, nullable=True)

    local_conveyance = Column(String(16), default='')
    employee_id = Column(Integer)
    manager_id  = Column(Integer, nullable=True)
    finance_id  = Column(Integer, nullable=True)

    def __repr__(self):
        return '<Tour {}: {}>'.format(self.id, self.name)
