#Flask Imports
from flask import Flask, render_template, request, redirect,jsonify, \
				  url_for, flash, make_response
from flask import session as login_session

#SQL ALchemy Imports
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

#Database import
from database_setup import Base, User, Goal, Comments

#Python imports
import random, string
import json
import requests

#OAUTH IMPORTS
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2



app = Flask(__name__)


#Connect to Database and create database session
engine = create_engine('sqlite:///mygoals.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def showIndex():
	''' Handler function for root page '''
	#return 'This page shows index with goals list'
	#goals = session.query(Goal).all()
	#user = session.query(User).all()
	#join User and Goal tabls with User.id == Goal.user_id
	userGoals = session.query(User,Goal).filter(User.id == Goal.user_id).all()
	return render_template('index.html', goals = userGoals)

@app.route('/login/')
def showLogin():
	''' Handler function for login page '''
	#return 'This page shows login buttons'
	return render_template('login.html')

@app.route('/<int:goal_id>/goal/')
def showGoal(goal_id):
	''' Handler function for a specific goal page'''
	#return 'This page shows a goal page'
	return render_template('showGoal.html')

@app.route('/user/<username>/')
def showProfile(username):
	''' Handler function for a specific user page '''
	#return 'This page shows a profile for %s' %username
	return render_template('profile.html')

@app.route('/<int:goal_id>/goal/new/')
def newGoal(goal_id):
	''' Handler function for a "create a new goal" page '''
	#return 'This page lets a user create a new goal'
	return render_template('newGoal.html')

@app.route('/<int:goal_id>/goal/edit/')
def editGoal(goal_id):
	''' Handler function for a "edit a goal" page '''
	#return 'This lets a user edit a goal'
	return render_template('editGoal.html')

@app.route('/<int:goal_id>/goal/delete/')
def deleteGoal(goal_id):
	''' Handler function for a "delete a goal" page '''
	#return 'This lets a user delete a goal'
	return render_template('deleteGoal.html')

@app.route('/<int:goal_id>/goal/complete/')
def completeGoal(goal_id):
	''' Handler function for a "mark goal as complete" page '''
	#return 'This lets a user mark a goal complete'
	return render_template('completeGoal.html')

@app.route('/user/<username>/edit/')
def editProfile(username):
	''' Handler function for a specific user to edit their profile '''
	#return 'This allows a user (%s) to edit their profile' %username
	return render_template('editProfile.html')

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)