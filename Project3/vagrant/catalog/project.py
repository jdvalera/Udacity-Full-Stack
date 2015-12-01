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

#OAUTH IMPORTS FOR GOOGLE
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2

#CSRF protection flask-seasurf
from flask.ext.seasurf import SeaSurf


# Google login settings
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "My Goals App"

# File upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'JPG'])

app = Flask(__name__)
# Config upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# max 16MB upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
# Config SeaSurf
csrf = SeaSurf(app)

#Connect to Database and create database session
engine = create_engine('sqlite:///mygoals.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Local permission system methods
def createUser(login_session):
	''' Helper function for creating a user '''
	newUser = User(username = login_session['username'], 
		email = login_session['email'], picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

def getUserID(email):
  ''' Helper function for getting a user ID with an email '''
  try:
    user = session.query(User).filter_by(email = email).one()
    return user.id
  except:
    return None

def getUserInfo(user_id):
  ''' Helper function that returns a user object '''
  user = session.query(User).filter_by(id = user_id).one()
  return user

# file upload method
def allowed_file(filename):
	''' Check if the file is allowed '''
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def showIndex():
	''' Handler function for root page '''
	# Join User and Goal tables with User.id == Goal.user_id
	# Show the 5 latest goals added
	userGoals = session.query(User,Goal).filter(and_(User.id == Goal.user_id,
	 Goal.isPrivate =="0")).order_by(desc(Goal.timestamp)).slice(0,5)
	return render_template('index.html', goals = userGoals)

@app.route('/login/', methods=['GET', 'POST'])
def showLogin():
	''' Handler function for login page '''
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
	 for x in xrange(32))
  	login_session['state'] = state
  	return render_template('login.html', STATE=state)

@app.route("/logout")
def logout():
	''' Handler function to log out a user '''
	#Check if user is logged in
	if 'username' not in login_session:
		return redirect('/login')
	gdisconnect()
	return redirect(url_for('showIndex'))

@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
  ''' Function for connecting using Google '''
  # Validate state token
  if request.args.get('state') != login_session['state']:
	  response = make_response(json.dumps('Invalid state parameter.'), 401)
	  response.headers['Content-Type'] = 'application/json'
	  return response
  # Obtain authorization code
  code = request.data

  try:
      # Upgrade the authorization code into a credentials object
      oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
      oauth_flow.redirect_uri = 'postmessage'
      credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
      response = make_response(
          json.dumps('Failed to upgrade the authorization code.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Check that the access token is valid.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
         % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
      response = make_response(json.dumps(result.get('error')), 500)
      response.headers['Content-Type'] = 'application/json'

  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
      response = make_response(
          json.dumps("Token's user ID doesn't match given user ID."), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
      response = make_response(
          json.dumps("Token's client ID does not match app's."), 401)
      print "Token's client ID does not match app's."
      response.headers['Content-Type'] = 'application/json'
      return response

  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
      response = make_response(json.dumps('Current user is already connected.'),
                               200)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Store the access token in the session for later use.
  login_session['credentials'] = credentials
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)
  data = answer.json()

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  #see if user exists if it doesn't make a new one
  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
  -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash("You are now logged in as %s" % login_session['username'])
  print "done!"
  return output

@app.route('/gdisconnect')
def gdisconnect():
    '''Function that handles Google auth disconnections'''
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have been logged out")
        return response
    else:
    	response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/<int:goal_id>/goal/', methods=['GET', 'POST'])
def showGoal(goal_id):
	''' Handler function for a specific goal page'''
	#Table join to be able to use User.username with userGoal variable
	userGoal = session.query(User, Goal).filter(and_(User.id == Goal.user_id, 
		Goal.id == goal_id)).one()

	comments = session.query(User,Comments).filter(and_(
		Comments.goal_id == goal_id, Comments.user_id == User.id)).all()

	if request.method == 'POST':

		if 'username' in login_session:
			newComment = Comments(content=request.form['content'],
							timestamp=datetime.datetime.utcnow(),
							user_id = login_session['user_id'],
							goal_id = userGoal.Goal.id)

			session.add(newComment)
			session.commit()
	
		return redirect(url_for('showGoal', goal_id = goal_id))
	else:
		return render_template('showGoal.html', goal = userGoal, 
			comments = comments)

@app.route('/user/<int:user_id>/')
def showProfile(user_id):
	''' Handler function for a specific user page '''
	user = session.query(User).filter_by(id = user_id).one()
	goals = session.query(Goal).filter_by(user_id = user_id).all()
	return render_template('profile.html', user = user, goals = goals)

@app.route('/user/<int:user_id>/goal/new/', methods=['GET','POST'])
def newGoal(user_id):
	''' Handler function for 'Create Goal' page '''

	user = session.query(User).filter_by(id = user_id).one()
	creator = getUserInfo(user.id)
	#Check if user is logged in
	if 'username' not in login_session:
		return redirect('/login')

	if creator.id != login_session['user_id']:
		return redirect('/')

	if request.method == 'POST':
		file = request.files['file']

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

		flash("New goal `%s` has been added" % newGoal.title)
		return redirect(url_for('showProfile', user_id = user_id))
	else:
		return render_template('newGoal.html')
	
@app.route('/user/<int:user_id>/goal/<int:goal_id>/edit/',
 methods=['GET', 'POST'])
def editGoal(user_id, goal_id):
	''' Handler function for a 'Edit Goal' page '''

	editedGoal = session.query(Goal).filter_by(id = goal_id).one()
	creator = getUserInfo(editedGoal.user_id)

	#Check if user is logged in
	if 'username' not in login_session:
		return redirect('/login')

	if creator.id != login_session['user_id']:
		return redirect('/')

	if request.method == 'POST':
		''' File Handler '''
		file = request.files['file']

		if file and allowed_file(file.filename):
			# if file exists
			# remove the previous picture
			if os.getcwd()+editedGoal.picture in os.getcwd()+'/static/uploads':
				os.remove(os.getcwd()+editedGoal.picture)

			filename = secure_filename(file.filename)
			ext = os.path.splitext(file.filename)[1]
			# Give random unique file name
			f_name = str(uuid.uuid4()) + ext
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
			#change user picture
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
		flash("Goal `%s` has been edited" % editedGoal.title)
		return redirect(url_for('showProfile', user_id = editedGoal.user_id))
	else:
		return render_template('editGoal.html', user_id = user_id, 
			goal_id = goal_id, item = editedGoal)

@app.route('/user/<int:user_id>/goal/<int:goal_id>/delete/',
	methods=['GET', 'POST'])
def deleteGoal(user_id, goal_id):
	''' Handler function for a 'Delete Goal' page '''

	goalToDelete = session.query(Goal).filter_by(id = goal_id).one()
	creator = getUserInfo(goalToDelete.user_id)

	if 'username' not in login_session:
		return redirect('/login')

	if creator.id != login_session['user_id']:
		return redirect('/')
	
	if request.method == 'POST':
		session.delete(goalToDelete)
		session.commit()
		flash("Goal `%s` has been successfully deleted" % goalToDelete.title)
		return redirect(url_for('showProfile', user_id = goalToDelete.user_id))
	else:
		return render_template('deleteGoal.html', goal = goalToDelete)

@app.route('/user/<int:user_id>/<int:goal_id>/goal/complete/',
	methods=['GET', 'POST'])
def completeGoal(user_id, goal_id):
	''' Handler function for a 'Completeing Goal' page '''
	goalToComplete = session.query(Goal).filter_by(id = goal_id).one()
	creator = getUserInfo(goalToComplete.user_id)

	if 'username' not in login_session:
		return redirect('/login')

	if creator.id != login_session['user_id']:
		return redirect('/')	

	if request.method == 'POST':
		goalToComplete.isDone = "1"
		session.commit()
		flash("Congratulations Goal `%s` has been completed!" 
			% goalToComplete.title)
		return redirect(url_for('showProfile', user_id=goalToComplete.user_id))
	else:

		return render_template('completeGoal.html', goal=goalToComplete)

@app.route('/user/<int:user_id>/edit/',
	methods=['GET', 'POST'])
def editProfile(user_id):
	''' Handler function for a specific user to edit their profile '''

	editedUser = session.query(User).filter_by(id = user_id).one()
	creator = getUserInfo(editedUser.id)

	#Check if user is logged in
	if 'username' not in login_session:
		return redirect('/login')

	if creator.id != login_session['user_id']:
		return redirect('/')

	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			# if file exists
			# remove the previous picture
			if os.getcwd()+editedUser.picture in os.getcwd()+'/static/uploads':
				os.remove(os.getcwd()+editedUser.picture)

			filename = secure_filename(file.filename)
			ext = os.path.splitext(file.filename)[1]
			# Give random unique file name
			f_name = str(uuid.uuid4()) + ext
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
			#change user picture
			editedUser.picture = os.path.join('/'+ app.config['UPLOAD_FOLDER'],
			 f_name)

		if request.form['description']:
			editedUser.desc = request.form['description']

		session.add(editedUser)
		session.commit()
		flash("Profile has been successfully edited!")
		return redirect(url_for('showProfile', 
			user_id = editedUser.id))
	else:
		return render_template('editProfile.html', user = editedUser)

#JSON APIs to view a User's  goals
@app.route('/JSON/')
def allGoalsJSON():
	''' JSON feed for all goals '''
	goals = session.query(Goal).all()

	return jsonify(Goals=[i.serialize for i in goals])

@app.route('/user/<int:user_id>/JSON/')
def userGoalsJSON(user_id):
	''' JSON feed to show a user's goals '''
	goals = session.query(Goal).filter_by(user_id = user_id).all()
	return jsonify(Goals=[i.serialize for i in goals])

@app.route('/XML/')
def allGoalsXML():
	''' XML feed for all goals '''
	goals = session.query(Goal).all()

	template = render_template('userGoals.xml', goals = goals)
	response = make_response(template)
	response.headers['Content-Type'] = 'application/xml'
	return response

@app.route('/user/<int:user_id>/XML/')
def userGoalsXML(user_id):
	''' XML feed for a user's goals'''
	goals = session.query(Goal).filter_by(user_id = user_id)
	template = render_template('userGoals.xml', goals = goals)
	response = make_response(template)
	response.headers['Content-Type'] = 'application/xml'
	return response
    

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)