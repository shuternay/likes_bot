from project.db import db
from models import User, Message, Like

db.create_tables([User, Message, Like])
