# SQLALCHEMY IMPORTS
from sqlalchemy import Column, ForeignKey, Integer, String, \
                       DATETIME, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key = True)
  username = Column(String(250))
  email = Column(String(250))
  picture = Column(String(250))
  desc = Column(String(250))
  goal = relationship('Goal', backref='author')
  comments = relationship('Comments', backref='author')
  
 
class Goal(Base):
    __tablename__ = 'goal'

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    timestamp = Column(DATETIME, default = func.current_timestamp())
    picture = Column(String(250))
    description = Column(String(250))
    isDone = Column(Integer)
    isPrivate = Column(Integer)
    user_id = Column(Integer,ForeignKey('user.id'))
    #user = relationship(User)
    comments = relationship('Comments', backref='goal')


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'title'         : self.title,
           'description'         : self.description,
           'id'         : self.id,
           'picture'  : self.picture,
           'time' : self.time
       }

class Comments(Base):
  __tablename__ = "comments"

  id = Column(Integer, primary_key=True)
  content = Column(String(500), nullable = False)
  timestamp = Column(DATETIME, default = func.current_timestamp())
  user_id = Column(Integer, ForeignKey('user.id'))
  goal_id = Column(Integer, ForeignKey('goal.id'))
  #user = relationship(User)
  #goal = relationship(Goal)


engine = create_engine('sqlite:///mygoals.db')
 

Base.metadata.create_all(engine)