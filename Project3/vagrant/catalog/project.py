#Flask Imports
from flask import Flask, render_template, request, redirect,jsonify, \
				  url_for, flash, make_response
from flask import session as login_session

#file upload
from werkzeug import secure_filename

#SQL ALchemy Imports
from sqlalchemy import create_engine, asc, and_, or_, desc
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
	userGoals = session.query(User,Goal).filter(and_(User.id == Goal.user_id,
	 Goal.isPrivate =="0")).order_by(desc(Goal.timestamp)).all()
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

@app.route('/user/<int:user_id>/')
def showProfile(user_id):
	''' Handler function for a specific user page '''
	#return 'This page shows a profile for %s' %username
	user = session.query(User).filter_by(id = user_id).one()
	goals = session.query(Goal).filter_by(user_id = user_id).all()
	return render_template('profile.html', user = user, goals = goals)

@app.route('/user/<int:user_id>/goal/new/', methods=['GET','POST'])
def newGoal(user_id):
	''' Handler function for a "create a new goal" page '''
	if request.method == 'POST':
		file = request.files['file']

		# if file:
		# 	if allowed_file(file.filename):
		# 		filename = secure_filename(file.filename)
		# 		ext = os.path.splitext(file.filename)[1]
		# 		# Give random unique file name
		# 		f_name = str(uuid.uuid4()) + ext
		# 		file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
		# 	else:
		# 		# If file is not a valid file type
		# 		response = make_response(json.dumps('Invalid file.'), 401)
		# 		response.headers['Content-Type'] = 'application/json'
		# 		print response

		# Give value to variable if checkbox is checked/unchecked
		if request.form.get('isDone') is None:
			done = "0"
		else:
			done = "1"

		if request.form.get('isPrivate') is None:
			private = "0"
		else:
			private = "1"


		newGoal = Goal(title=request.form['title'],
				   timestamp=datetime.datetime.utcnow(),
				   description=request.form['description'],
				   isDone=done,
				   isPrivate=private,
				   user_id = user_id)

		#check if user uploaded a file before entering file into database
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			ext = os.path.splitext(file.filename)[1]
			# Give random unique file name
			f_name = str(uuid.uuid4()) + ext
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
			newGoal.picture = os.path.join('/'+ app.config['UPLOAD_FOLDER'],
			 f_name)

		session.add(newGoal)
		session.commit()
		return redirect(url_for('showProfile', user_id = user_id))
	else:
		return render_template('newGoal.html')
	#return 'This page lets a user create a new goal'
	
@app.route('/user/<int:user_id>/goal/<int:goal_id>/edit/',
 methods=['GET', 'POST'])
def editGoal(user_id, goal_id):
	''' Handler function for a "edit a goal" page '''
	#return 'This lets a user edit a goal'.

	editedGoal = session.query(Goal).filter_by(id = goal_id).one()
	if request.method == 'POST':
		''' File Handler '''
		file = request.files['file']

		# if file:
		# 	if allowed_file(file.filename):
		# 		filename = secure_filename(file.filename)
		# 		ext = os.path.splitext(file.filename)[1]
		# 		# Give random unique file name
		# 		f_name = str(uuid.uuid4()) + ext
		# 		file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
		# 	else:
		# 		# If file is not a valid file type
		# 		response = make_response(json.dumps('Invalid file.'), 401)
		# 		response.headers['Content-Type'] = 'application/json'
		# 		return response

		if file and allowed_file(file.filename):
			#remove the previous picture
			os.remove(os.getcwd()+editedGoal.picture)

			filename = secure_filename(file.filename)
			ext = os.path.splitext(file.filename)[1]
			# Give random unique file name
			f_name = str(uuid.uuid4()) + ext
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
			editedGoal.picture = os.path.join('/'+ app.config['UPLOAD_FOLDER'],
			 f_name)

		if request.form['title']:
			editedGoal.title = request.form['title']
			
		if request.form['description']:
			editedGoal.description = request.form['description']

		if request.form.get('isDone') is None:
			done = "0"
		else:
			done = "1"
		editedGoal.isDone = done

		if request.form.get('isPrivate') is None:
			private = "0"
		else:
			private = "1"
		editedGoal.isPrivate = private

		session.add(editedGoal)
		session.commit()
		return redirect(url_for('showProfile', user_id = editedGoal.user_id))
	else:
		return render_template('editGoal.html', user_id = user_id, 
			goal_id = goal_id, item = editedGoal)

@app.route('/user/<int:user_id>/goal/<int:goal_id>/delete/',
	methods=['GET', 'POST'])
def deleteGoal(user_id, goal_id):
	''' Handler function for a "delete a goal" page '''
	#return 'This lets a user delete a goal'
	goalToDelete = session.query(Goal).filter_by(id = goal_id).one()
	if request.method == 'POST':
		session.delete(goalToDelete)
		session.commit()
		return redirect(url_for('showProfile', user_id = goalToDelete.user_id))
	else:
		return render_template('deleteGoal.html', goal = goalToDelete)

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