from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
salt = '26ecf3edb2e143c69ec0119e831c8c67' # uuid.uuid4().hex

from model.user import User
from model.tour import Tour
from model.session import Session
