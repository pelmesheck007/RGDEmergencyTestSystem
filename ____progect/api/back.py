from sqlalchemy import *
from sqlalchemy.orm import  sessionmaker, declarative_base
engine = create_engine('sqlite:///db.db')

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(20))
    password = Column(String(20))
    nickname = Column(String(20))
    date_birth = Column(Date)
    about_me = Column(Text)
    number_phone = Column(String(20))
    email = Column(String(20))
    gender = Column(Integer)
    photo = Column(Integer)


class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    id_sender = Column(Integer, ForeignKey('user.id'))
    id_recipient = Column(Integer, ForeignKey('user.id'))
    status = Column(Integer)


class Friend(Base):
    __tablename__ = 'friend'
    id = Column(Integer, primary_key=True)
    id_user1 = Column(Integer, ForeignKey("user.id"))
    id_user2 = Column(Integer, ForeignKey("user.id"))
    status = Column(Integer)


class Hobby(Base):
    __tablename__ = 'hobby'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))


class User_hobby(Base):
    __tablename__ = 'user_hobby'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey("user.id"))
    id_hobby = Column(Integer, ForeignKey("hobby.id"))


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    id_sender = Column(Integer, ForeignKey("user.id"))
    id_recipient = Column(Integer, ForeignKey("user.id"))
    date = Column(Date)
    time = Column(String(10))
    message = Column(Text)


Base.metadata.create_all(engine)

Sessionlocal = sessionmaker(bind=engine)
session = Sessionlocal()

