from project.db import db
from models import User, Message, Like


def create_tables():
    db.create_tables([User, Message, Like])
