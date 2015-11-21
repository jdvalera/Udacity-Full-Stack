#Flask Imports
from flask import Flask, render_template, request, redirect,jsonify, \
				  url_for, flash, make_response
from flask import session as login_session

#file upload
from werkzeug import secure_filename

#SQL ALchemy Imports
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

#Database import
from database_setup import Base, User, Goal, Comments

#Python imports
import random, string, json, requests, datetime, os, uuid

#OAUTH IMPORTS
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# max 16MB upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 


#Connect to Database and create database session
engine = create_engine('sqlite:///mygoals.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def allowed_file(filename):
	''' Check if the file is allowed '''
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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

@app.route('/user/<int:user_id>/goal/new/', methods=['GET','POST'])
def newGoal(user_id):
	''' Handler function for a "create a new goal" page '''
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			ext = os.path.splitext(file.filename)[1]
			# Give random unique file name
			f_name = str(uuid.uuid4()) + ext
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
		newGoal = Goal(title=request.form['title'],
				   timestamp=datetime.datetime.utcnow(),
				   picture=os.path.join(app.config['UPLOAD_FOLDER'], f_name),
				   description=request.form['description'],
				   isDone=request.form.get('isDone'),
				   isPrivate=request.form.get('isPrivate'),
				   user_id = user_id)
		session.add(newGoal)
		session.commit()
		return redirect(url_for('showIndex'))
	else:
		return render_template('newGoal.html')
	#return 'This page lets a user create a new goal'
	
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