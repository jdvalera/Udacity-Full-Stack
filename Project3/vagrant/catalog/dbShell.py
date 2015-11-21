from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from puppies import Base, User, Goal, Comments
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random


engine = create_engine('sqlite:///mygoals.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


#Add User
User1 = User(username="TinyTim", email="tinytim@gmail.com",
 picture="https://pbs.twimg.com/profile_images/2671170543\
 /18debd694829ed78203a5a36dd364160_400x400.png",
 desc="I am TinyTim!")

User2 = User(username="LadyLay", email="ladylay@gmail.com",
 picture="https://pbs.twimg.com/profile_images/2671170543\
 /18debd694829ed78203a5a36dd364160_400x400.png",
 desc="I am LadyLay!")

session.add(User1)
session.add(User2)
session.commit()

Goal1 = Goal(title="Climb Mount Everest!", timestamp=datetime.datetime.utcnow(),
       picture = "https://pbs.twimg.com/profile_images/2671170543\
       /18debd694829ed78203a5a36dd364160_400x400.png",
       description="I want to climb this mountain!",
       isDone="0", isPrivate="0", user_id="1")

Goal2 = Goal(title="Climb Mount Fiji!", timestamp=datetime.datetime.utcnow(),
       picture = "https://pbs.twimg.com/profile_images/2671170543\
       /18debd694829ed78203a5a36dd364160_400x400.png",
       description="I want to climb this mountain!",
       isDone="0", isPrivate="0", user_id="2")

session.add(Goal1)
session.add(Goal2)
session.commit()