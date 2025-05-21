from datetime import datetime
import uvicorn
from fastapi import FastAPI, Body
from sqlalchemy.testing import in_

from back import *
from sqlalchemy import and_
app = FastAPI()
import requests
# uvicorn main:app --reload


class AllEquests:
    @staticmethod
    @app.get("/proverka")
    async def proverka(data=Body()):
        for us in session.query(User).all():
            if us.login == data["login"] or us.nickname == data["nickname"]:
                return True

    @staticmethod
    @app.post("/reg")
    async def reg(data=Body()):
        try:
            user = User(
                login=data["login"],
                password=data["password"],
                nickname=data["nickname"],
                date_birth=datetime.strptime(data["date_birth"], '%Y-%m-%d').date(),
                about_me=data["about_me"],
                number_phone=data["number_phone"],
                email=data["email"],
                gender=data["gender"]
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            print(e)

    @staticmethod
    @app.put('/updatefriend')
    async def update_friend(id_user1, id_user2):
        friend = session.query(Friend).filter(or_(and_(Friend.id_user1 == id_user1, Friend.id_user2 == id_user2),and_(Friend.id_user1 == id_user2, Friend.id_user2 == id_user1))).one()
        friend.status = -1
        session.commit()
        session.refresh(friend)
        return friend

    @staticmethod
    @app.get("/auf")
    async def auf(login, password):
        return session.query(User).filter(and_(User.login == login, User.password == password)).one()

    @staticmethod
    @app.get("/peo")
    async def all_user(date):
        date_birth = datetime.strptime(date, '%Y-%m-%d').date()
        high = datetime.strptime(date, '%Y-%m-%d').date().replace(year=date_birth.year + 10)
        down = datetime.strptime(date, '%Y-%m-%d').date().replace(year=date_birth.year - 10)
        return session.query(User).filter(between(User.date_birth, down, high)).all()

    @staticmethod
    @app.get("/proverkafr")
    async def proverka_friend(data=Body()):
        for us in session.query(Friend).all():
            if (us.id_user1 == data["id_user1"] and us.id_user2 == data["id_user2"]) or (
                    us.id_user1 == data["id_user2"] and us.id_user2 == data["id_user1"]):
                return True

    @staticmethod
    @app.get("/hobby")
    async def all_hobby():
        return session.query(Hobby).all()

    @staticmethod
    @app.post("/hobbyadd")
    async def hobby_add(data=Body()):
        try:
            user_body = User_hobby(
                id_user=data["id_user"],
                id_hobby=data["id_hobby"]
            )
            session.add(user_body)
            session.commit()
            session.refresh(user_body)
            return user_body
        except Exception as e:
            print(e)

    @staticmethod
    @app.get("/hobbyuser")
    async def hobby_user(id_user):
        return session.query(User_hobby).filter(User_hobby.id_user == id_user).all()

    @staticmethod
    @app.post("/friendadd")
    async def friend_add(data=Body()):
        try:
            friend = Friend(
                id_user1=data["id_user1"],
                id_user2=data["id_user2"],
                status=data["status"]
            )
            session.add(friend)
            session.commit()
            session.refresh(friend)
            return friend
        except Exception as e:
            print(e)

    @staticmethod
    @app.get("/myfriends")
    async def my_friends(id_user):
        friends = (
            session.query(User.nickname)
            .join(Friend, or_(Friend.id_user1 == User.id, Friend.id_user2 == User.id))
            .filter(
                and_(
                    and_(or_(Friend.id_user1 == id_user, Friend.id_user2 == id_user), Friend.status == 1),
                    User.id != id_user
                )
            )
            .distinct()
            .all()
        )
        friends_list = [friend.nickname for friend in friends]

        return friends_list

    @staticmethod
    @app.post("/chatot")
    async def chat_add(data=Body()):
        try:
            chat = Chat(
                id_sender=data["id_sender"],
                id_recipient=data["id_recipient"],
                date=datetime.strptime(data["date"], '%Y-%m-%d').date(),
                time=data["time"],
                message=data["message"]
            )
            session.add(chat)
            session.commit()
            session.refresh(chat)
            return chat
        except Exception as e:
            print(e)

    @staticmethod
    @app.get("/chat")
    async def chat_all(id_sender: int, id_recipient: int):
        return session.query(Chat).filter(or_((and_(Chat.id_sender == id_sender, Chat.id_recipient == id_recipient)), (
            and_(Chat.id_sender == id_recipient, Chat.id_recipient == id_sender)))).all()

    @staticmethod
    @app.delete("/chatdel/{id_sender}/{id_recipient}")
    async def chat_del(id_sender: int, id_recipient: int):
        answer = await AllEquests.chat_all(id_sender, id_recipient)
        for i in answer:
            session.delete(i)
        session.commit()
        return {"status": "success"}

    @staticmethod
    @app.put('/update')
    async def update(user_id, data=Body()):
        user = session.query(User).filter(User.id == user_id).one()
        if "login" in data:
            user.login = data["login"]
        if "password" in data:
            user.password = data["password"]
        if "nickname" in data:
            user.nickname = data["nickname"]
        if "about_me" in data:
            user.about_me = data["about_me"]
        if "number_phone" in data:
            user.number_phone = data["number_phone"]
        if "email" in data:
            user.email = data["email"]
        session.commit()
        session.refresh(user)
        return user

session.close()
