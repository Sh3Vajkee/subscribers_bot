from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text

from db.base import Base


class Subscribers(Base):
    __tablename__ = 'subscribers'

    user_id = Column(BigInteger, primary_key=True)
    is_paid = Column(Boolean, default=False)
    last_uuid = Column(String(100))


class SubBuyers(Base):
    __tablename__ = 'subbuyers'

    user_id = Column(BigInteger, primary_key=True)
    balance = Column(Integer, default=0)
    status = Column(String, default="left")
