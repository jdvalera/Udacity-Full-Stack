#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

import logging
from datetime import datetime
from datetime import time

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import ConflictException
from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import StringMessage
from models import BooleanMessage
from models import Conference
from models import ConferenceForm
from models import ConferenceForms
from models import ConferenceQueryForm
from models import ConferenceQueryForms
from models import TeeShirtSize
from models import Session
from models import SessionForm
from models import SessionForms
from models import Speaker
from models import SpeakerForm
from models import SpeakerForms
from models import FeaturedSpeakerForm

from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE

from utils import getUserId

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
MEMCACHE_FEATURED_SPEAKER_KEY = "FEATURED_SPEAKER"
ANNOUNCEMENT_TPL = ('Last chance to attend! The following conferences '
                    'are nearly sold out: %s')
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": [ "Default", "Topic" ],
}

SESSION_DEFAULTS = {
    "highlights": "Not Specified",
    "duration": '0',
    "typeOfSession": "Not Specified",
}

OPERATORS = {
            'EQ':   '=',
            'GT':   '>',
            'GTEQ': '>=',
            'LT':   '<',
            'LTEQ': '<=',
            'NE':   '!='
            }

FIELDS =    {
            'CITY': 'city',
            'TOPIC': 'topics',
            'MONTH': 'month',
            'MAX_ATTENDEES': 'maxAttendees',
            }

CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
)

CONF_POST_REQUEST = endpoints.ResourceContainer(
    ConferenceForm,
    websafeConferenceKey=messages.StringField(1),
)

SESS_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
    )

SPKR_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    )

SPKR_GET_SESS_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeKey=messages.StringField(1),
    )

SESS_TYPE_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeConferenceKey=messages.StringField(1),
    typeOfSession=messages.StringField(2),
    )

WISH_POST_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeSessionKey=messages.StringField(1),
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api(name='conference', version='v1', audiences=[ANDROID_AUDIENCE],
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID, \
    ANDROID_CLIENT_ID, IOS_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""


#------------------------SESSION WISHLIST----------------------
    @endpoints.method(WISH_POST_REQUEST, SessionForm,
            path='sessions/{websafeSessionKey}',
            http_method='POST', name='addSessionToWishlist')
    def addSessionToWishlist(self, request):
        """Add a session to user's wishlist"""
        user = endpoints.get_current_user()

        #check if logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        #grab user profile
        prof = self._getProfileFromUser()

        #grab session using urlsafe key
        wsck = request.websafeSessionKey
        sess = ndb.Key(urlsafe=wsck).get()

        #check if session exists
        if not sess:
            raise endpoints.NotFoundException(
                'No Session found with key: %s' % wsck)

        # check if user already registered otherwise add
        if wsck in prof.sessionsKeysToAttend:
            raise ConflictException(
                "You have already registered for this session")

        # register user, take away one seat
        prof.sessionsKeysToAttend.append(wsck)

        prof.put()
        return self._copySessionToForm(sess)

    @endpoints.method(message_types.VoidMessage, SessionForms,
            path='sessions/attending',
            http_method='GET', name='getSessionsInWishlist')
    def getSessionsInWishlist(self, request):
        """Get a list of sessions that a user has registered for."""
        user = endpoints.get_current_user()

        #check if logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        #get profile from user
        prof = self._getProfileFromUser()

        #grab session keys that a user has registered for
        sess_keys = [ndb.Key(urlsafe=wsck) 
        for wsck in prof.sessionsKeysToAttend]

        #turn keys into instances
        sessions = ndb.get_multi(sess_keys)

        #return all sessions on the user's wishlist
        return SessionForms(items=[self._copySessionToForm(s) 
            for s in sessions])


    @endpoints.method(WISH_POST_REQUEST, BooleanMessage,
            path='sessions/{websafeSessionKey}/delete',
            http_method='DELETE', name='deleteSessionInWishlist')
    def deleteSessionInWishlist(self, request):
        """Removes the session from the user's list of 
        sessions they are attending"""
        #boolean value
        retval = None
        #check if logged in
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        #grab user profile
        prof = self._getProfileFromUser()

        #use webSafeSessionKey to grab session instance
        wsck = request.websafeSessionKey
        sess = ndb.Key(urlsafe=wsck).get()

        #check if session exists
        if not sess:
            raise endpoints.NotFoundException(
                'No Session found with key: %s' % wsck)

        # Check if session is in user's wishlist then delete session from list
        if wsck in prof.sessionsKeysToAttend:
            prof.sessionsKeysToAttend.remove(wsck)
            retval = True

        prof.put()
        return BooleanMessage(data=retval)



#------------------------SPEAKER OBJECTS-----------------------
    def _copySpeakerToForm(self, spkr):
        """Copy relevant fields from Speaker to SpeakerForm."""
        sf = SpeakerForm()
        for field in sf.all_fields():
            if hasattr(spkr, field.name):
                setattr(sf, field.name, getattr(spkr, field.name))
            #show the websafekey by using spkr.key.urlsafe()
            elif field.name == "websafeKey":
                setattr(sf, field.name, spkr.key.urlsafe())
        sf.check_initialized()
        return sf

    def _createSpeakerObject(self, request):
        """Create or update Speaker object, returning SpeakerForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()

        #check if logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        #check if the user specified a name
        if not request.name:
            raise endpoints.BadRequestException("Speaker 'name' field required")

        data = {field.name: getattr(request, field.name) 
        for field in request.all_fields()}
        #delete, doesn't exist in model
        del data['websafeKey']

        Speaker(**data).put()

        return request

    @endpoints.method(SpeakerForm, SpeakerForm, path='speaker',
            http_method='POST', name='createSpeaker')
    def createSpeaker(self, request):
        """Create new Speaker"""
        return self._createSpeakerObject(request)


    @endpoints.method(SPKR_GET_REQUEST, SpeakerForms,
            path='speakers',
            http_method='GET', name='getSpeakers')
    def getSpeakers(self, request):
        """Return speakers"""

        spkrs = Speaker.query().order(Speaker.name)

        return SpeakerForms(items=[self._copySpeakerToForm(s) for s in spkrs])

#------ Session Objects ------------------------------------
    def _copySessionToForm(self, sess):
        """Copy relevant fields from Session to SessionForm."""
        sf = SessionForm()
        for field in sf.all_fields():
            if hasattr(sess, field.name):
                # convert Date to date string; just copy others
                if field.name in ['startTime', 'date']:
                    setattr(sf, field.name, str(getattr(sess, field.name)))
                #get the websafe key from session to display
                elif field.name == 'speakerKeys':
                    spkrs = getattr(sess, field.name)
                    spkrs = [s.urlsafe() for s in spkrs]
                    setattr(sf, field.name, spkrs)
                else:
                    setattr(sf, field.name, getattr(sess, field.name))
            #show's the speaker's names
            if field.name == 'speakerNames':
                spkrs = getattr(sess, 'speakerKeys')
                spkrs = [s.get().name for s in spkrs]
                setattr(sf, field.name, spkrs)
            if field.name == 'websafeSessionKey':
                webKey = sess.key.urlsafe()
                setattr(sf, field.name, webKey)

        sf.check_initialized()
        return sf

    def _createSessionObject(self, request):
        """Create or update Session object, returning SessionForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()

        #check if logged in
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        #Name is a required field
        if not request.name:
            raise endpoints.BadRequestException("Session 'name' field required")

        #WebsafeConferenceKey is a required field
        if not request.websafeConferenceKey:
            raise endpoints.BadRequestException("websafeConferenceKey\
             is required")

        #grab conference instance from key
        wsck = request.websafeConferenceKey
        conf = ndb.Key(urlsafe=wsck).get()

        #check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can create sessions.')

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) 
        for field in request.all_fields()}

        # add default values for those missing 
        #(both data model & outbound Message)
        for df in SESSION_DEFAULTS:
            if data[df] in (None, []):
                data[df] = SESSION_DEFAULTS[df]
                setattr(request, df, SESSION_DEFAULTS[df])

        # convert dates from strings to Date objects
        if data['date']:
            data['date'] = \
            datetime.strptime(data['date'][:10], "%Y-%m-%d").date()
            #Date has to fal between conference dates
            if not conf.startDate <= data['date'] <= conf.endDate: 
               raise endpoints.BadRequestException( 
                    'Date must fall within conference dates.')

        if data['speakerKeys']:
            speakers = data['speakerKeys']
            data['speakerKeys'] = \
            [ndb.Key(urlsafe=s) for s in data['speakerKeys']] 


        # convert time from strings to Time objects
        if data['startTime']:
            data['startTime'] = \
            datetime.strptime(data['startTime'][:5], "%H:%M").time()


        #generate session id using conference key as parent
        #generate session key using session id and parent key
        s_id = Session.allocate_ids(size=1, parent=conf.key)[0]
        s_key = ndb.Key(Session, s_id, parent=conf.key)
        data['key'] = s_key
        #delete, these fields do not exist in model
        del data['websafeConferenceKey']
        del data['speakerNames']
        del data['websafeSessionKey']

        Session(**data).put()

        #if speaker field present queue task
        #create task that determines featured speaker
        if data['speakerKeys']:
            taskqueue.add(params={'websafeConferenceKey':wsck,
                'speakers':speakers},
                url='/tasks/set_featured_speaker'
            )
        return request

    @endpoints.method(SESS_GET_REQUEST, SessionForms,
            path='conference/{websafeConferenceKey}/sessions',
            http_method='GET', name='getConferenceSessions')
    def getConferenceSessions(self, request):
        """Return requested sessions (by websafeConferenceKey)."""
        # get Conference object from request; bail if not found
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' 
                % request.websafeConferenceKey)
        #Call on conference property that returns a list of sessions
        sess = conf.sessions
        return SessionForms(items=[self._copySessionToForm(s) for s in sess])

    @endpoints.method(SESS_TYPE_REQUEST, SessionForms, 
        path='/{websafeConferenceKey}/session_by_type/{typeOfSession}',
            http_method='GET', name='getSessionsByType')
    def getConferenceSessionsByType(self, request):
        """Return all sessions of a conference by the type of session"""
        
        data = {field.name: getattr(request, field.name) 
        for field in request.all_fields()}
        typeOfSession = data['typeOfSession']

        #fetch conference from key
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()

        #Check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with this key: %s' 
                % request.websafeConferenceKey)

        #Create ancestor query for all key matches for this conference
        sessions = Session.query(Session.typeOfSession == typeOfSession,
            ancestor=conf.key)

        return SessionForms(
                items=[self._copySessionToForm(session) for session in sessions]
            )


    @endpoints.method(SPKR_GET_SESS_REQUEST, SessionForms, 
        path='/{websafeKey}/session',
            http_method='GET', name='getSessionsBySpeaker')
    def getSessionsBySpeaker(self, request):
        """Return Sessions By Speaker"""
        #grab speaker instance using key
        spkr = ndb.Key(urlsafe=request.websafeKey).get()
        #check if speaker exists
        if not spkr:
            raise endpoints.NotFoundException(
                'No speaker found with key: %s' % request.websafeKey)
        return SessionForms(items=[self._copySessionToForm(s) 
            for s in spkr.session])

    @endpoints.method(SESS_GET_REQUEST, SessionForms, 
            path='/{websafeConferenceKey}/popular/sessions',
            http_method='GET', name='getSessionsByPopularity')
    def getSessionsByPopularity(self, request):
        """Return sessions by wishlist popularity"""

        #fetch conference from key
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()

        #Check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with this key: %s' 
                % request.websafeConferenceKey)

        #Create ancestor query for all key matches for this conference
        sessions = Session.query(ancestor=conf.key).fetch()

        session_list = []
        #for every session inside a conference count how many times each session
        #is added to someone's wishlist. Append to list of dictionaries.
        for sess in sessions:
            count = Profile.query().filter(Profile.sessionsKeysToAttend
                == sess.key.urlsafe()).count()
            session_list.append(
                {'session':sess,
                 'count': count
                 }
                )
        #sort list in descending order using 'count' key
        session_list = sorted(session_list, 
            key=lambda sess: sess['count'], reverse=True)


        return SessionForms(items=[self._copySessionToForm(s['session']) 
            for s in session_list])

    @endpoints.method(message_types.VoidMessage, SessionForms,
            http_method='GET', name='getNonWorkshopBeforeSeven')
    def getNonWorkshopBeforeSeven(self, request):
        """Returns non-workshop sessions before 7pm(19:00)"""
        #query sessions before 7pm and make sure field is not None
        sess = Session.query()
        time = datetime.strptime("19:00", "%H:%M").time()
        sess = sess.filter(Session.startTime <= time)
        sess = sess.filter(Session.startTime != None)
        sessions = []
        #use python to filter out sessions with type 'Workshop'
        for s in sess:
            if(s.typeOfSession.lower() != 'Workshop'.lower()):
                sessions.append(s)
        return SessionForms(items=[self._copySessionToForm(s) 
            for s in sessions])

    @endpoints.method(WISH_POST_REQUEST, SpeakerForms, 
        path='session/{websafeSessionKey}/speakers',
            http_method='GET', name='showSpeakerInfo')
    def showSpeakerInfo(self, request):
        """Return Speakers by session"""
        #grab session instance using websafeSessionkey
        sess = ndb.Key(urlsafe=request.websafeSessionKey).get()
        #populate list with speakers from the session
        spkr_keys = [s for s in sess.speakerKeys]

        return SpeakerForms(items=[self._copySpeakerToForm(s.get()) 
            for s in spkr_keys])


    @endpoints.method(SessionForm, SessionForm, path='session',
            http_method='POST', name='createSession')
    def createSession(self, request):
        """Create new Session"""
        return self._createSessionObject(request)

# - - - Conference objects - - - - - - - - - - - - - - - - -
    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='/popular/conferences',
            http_method='GET', name='getConferencesByPopularity')
    def getConferencesByPopularity(self, request):
        """Return conferences by popularity"""
         #fetch conference from key
        conf = Conference.query().fetch()

        #Check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with this key: %s' 
                % request.websafeConferenceKey)
        conf_list = []

        for c in conf:
            count = Profile.query().filter(Profile.conferenceKeysToAttend 
                == c.key.urlsafe()).count()
            conf_list.append(
                {'conf':c,
                 'count':count
                }
                )
        conf_list = sorted(conf_list, 
            key=lambda conf: conf['count'], reverse=True)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, c.organizerUserId)) for c in conf]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
                items=[self._copyConferenceToForm(c['conf'], 
                    names[c['conf'].organizerUserId]) for c in \
                conf_list]
        )


    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf


    def _createConferenceObject(self, request):
        """Create or update Conference object, returning 
        ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        if not request.name:
            raise endpoints.BadRequestException("Conference 'name' \
                field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field 
        in request.all_fields()}
        del data['websafeKey']
        del data['organizerDisplayName']

        # add default values for those missing (both data model & outbound Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['startDate']:
            data['startDate'] = datetime.strptime(data['startDate'][:10],\
             "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = datetime.strptime(data['endDate'][:10],\
             "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference, send email to organizer confirming
        # creation of Conference & return (modified) ConferenceForm
        Conference(**data).put()
        taskqueue.add(params={'email': user.email(),
            'conferenceInfo': repr(request)},
            url='/tasks/send_confirmation_email'
        )
        return request


    @ndb.transactional()
    def _updateConferenceObject(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) 
        for field in request.all_fields()}

        # update existing conference
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        # check that conference exists
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' 
                % request.websafeConferenceKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('startDate', 'endDate'):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                    if field.name == 'startDate':
                        conf.month = data.month
                # write to Conference object
                setattr(conf, field.name, data)
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    @endpoints.method(ConferenceForm, ConferenceForm, path='conference',
            http_method='POST', name='createConference')
    def createConference(self, request):
        """Create new conference."""
        return self._createConferenceObject(request)


    @endpoints.method(CONF_POST_REQUEST, ConferenceForm,
            path='conference/{websafeConferenceKey}',
            http_method='PUT', name='updateConference')
    def updateConference(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._updateConferenceObject(request)


    @endpoints.method(CONF_GET_REQUEST, ConferenceForm,
            path='conference/{websafeConferenceKey}',
            http_method='GET', name='getConference')
    def getConference(self, request):
        """Return requested conference (by websafeConferenceKey)."""
        # get Conference object from request; bail if not found
        conf = ndb.Key(urlsafe=request.websafeConferenceKey).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s'
                 % request.websafeConferenceKey)
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='getConferencesCreated',
            http_method='POST', name='getConferencesCreated')
    def getConferencesCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, 
                getattr(prof, 'displayName')) for conf in confs]
        )


    def _getQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "maxAttendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"], 
                filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q


    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name) 
            for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException("Filter contains\
                 invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
                # track the field on which the inequality operation is performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException("Inequality filter is\
                     allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)


    @endpoints.method(ConferenceQueryForms, ConferenceForms,
            path='queryConferences',
            http_method='POST',
            name='queryConferences')
    def queryConferences(self, request):
        """Query for conferences."""
        conferences = self._getQuery(request)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, conf.organizerUserId)) 
        for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
                items=[self._copyConferenceToForm(conf,
                 names[conf.organizerUserId]) for conf in conferences]
        )


# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf, field.name, getattr(TeeShirtSize, 
                        getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf


    def _getProfileFromUser(self):
        """Return user Profile from datastore, 
        creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key = p_key,
                displayName = user.nickname(),
                mainEmail= user.email(),
                teeShirtSize = str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()

        return profile      # return Profile


    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
                        prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)


    @endpoints.method(message_types.VoidMessage, ProfileForm,
            path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()


    @endpoints.method(ProfileMiniForm, ProfileForm,
            path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)


# ---------------------------FEATURED SPEAKER-----------------
    @staticmethod
    def _cacheFeaturedSpeaker(request):
        """Assign Featured Speaker to memcache.
        """
        #use websafeConferenceKey to grab an instance of conference
        wsck = ndb.Key(urlsafe=request.get('websafeConferenceKey'))
        conf = wsck.get()
        #fetch all sessions from a given conference
        sessions = Session.query(ancestor = wsck).fetch()


        #request.get_all() gets the whole value of a list per value
        #while request.get() gets the values character per character
        added_speakers = request.get_all('speakers')
        added_speaker_keys = [ndb.Key(urlsafe=s) for s in added_speakers]
        
        speakers = {}
        #for every session in sessions list
        for sess in sessions:
            #for each speaker key in speakerKeys list
            for s in sess.speakerKeys:
                # check if the speaker key is the one just recently added
                if s in added_speaker_keys:
                    if s in speakers.keys():
                        #append sessions to dictionary
                        speakers[s]['sessions'].append(sess)
                        #increment session count of dictionary
                        speakers[s]['count'] += 1
                    else:
                        #initialize dictionary if key isn't already present
                        speakers[s] = {}
                        speakers[s]['sessions'] = [sess]
                        speakers[s]['count'] = 1

        #initialize featured speaker dictionary
        featured_speaker = {'sessions':[], 'speaker':"",'num_sessions':0}

        #for every speaker in speakers list
        for s in speakers:
            # check if speaker has the most sessions
            if(speakers[s]['count'] >= featured_speaker['num_sessions']):
                #if the speaker has more sessions overwrite previous speaker
                featured_speaker['sessions'] = speakers[s]['sessions']
                featured_speaker['num_sessions'] = speakers[s]['count']
                featured_speaker['speaker'] = s.get().name


        #check if speaker has 2 or more sessions (req. to be featured speaker)
        if featured_speaker['num_sessions'] > 1:
            #populate featured_message dictionary
            featured_message = {'featured_speaker': featured_speaker['speaker'],
                                'sessions': [s.name for s in 
                                featured_speaker['sessions']],
                                'conference': conf.name}
            #set memcache with key and dictionary
            memcache.set(MEMCACHE_FEATURED_SPEAKER_KEY, featured_message)

        return featured_message


    @endpoints.method(message_types.VoidMessage, FeaturedSpeakerForm,
            path='featured_speaker/get',
            http_method='GET', name='getFeaturedSpeaker')
    def getFeaturedSpeaker(self, request):
        """Return Speaker from memcache."""
        #if empty memcache
        if memcache.get(MEMCACHE_FEATURED_SPEAKER_KEY) == None:
            return FeaturedSpeakerForm(
            featuredSpeaker="",
            sessions=[],
            conference="")
        #populate FeaturedSpeakerForm if memcache is not empty
        return FeaturedSpeakerForm(
            featuredSpeaker=\
            memcache.get(MEMCACHE_FEATURED_SPEAKER_KEY)['featured_speaker'] \
            or "",
            sessions=memcache.get(MEMCACHE_FEATURED_SPEAKER_KEY)['sessions']\
            or [],
            conference=\
            memcache.get(MEMCACHE_FEATURED_SPEAKER_KEY)['conference']) or ""

    


# - - - Announcements - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def _cacheAnnouncement():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        confs = Conference.query(ndb.AND(
            Conference.seatsAvailable <= 5,
            Conference.seatsAvailable > 0)
        ).fetch(projection=[Conference.name])

        if confs:
            # If there are almost sold out conferences,
            # format announcement and set it in memcache
            announcement = ANNOUNCEMENT_TPL % (
                ', '.join(conf.name for conf in confs))
            memcache.set(MEMCACHE_ANNOUNCEMENTS_KEY, announcement)
        else:
            # If there are no sold out conferences,
            # delete the memcache announcements entry
            announcement = ""
            memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)

        return announcement


    @endpoints.method(message_types.VoidMessage, StringMessage,
            path='conference/announcement/get',
            http_method='GET', name='getAnnouncement')
    def getAnnouncement(self, request):
        """Return Announcement from memcache."""
        return StringMessage(
            data=memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY) or "")


# - - - Registration - - - - - - - - - - - - - - - - - - - -

    @ndb.transactional(xg=True)
    def _conferenceRegistration(self, request, reg=True):
        """Register or unregister user for selected conference."""
        retval = None
        prof = self._getProfileFromUser() # get user Profile

        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeConferenceKey
        conf = ndb.Key(urlsafe=wsck).get()
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % wsck)

        # register
        if reg:
            # check if user already registered otherwise add
            if wsck in prof.conferenceKeysToAttend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seatsAvailable <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conferenceKeysToAttend.append(wsck)
            conf.seatsAvailable -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsck in prof.conferenceKeysToAttend:

                # unregister user, add back one seat
                prof.conferenceKeysToAttend.remove(wsck)
                conf.seatsAvailable += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='conferences/attending',
            http_method='GET', name='getConferencesToAttend')
    def getConferencesToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._getProfileFromUser() # get user Profile
        conf_keys = [ndb.Key(urlsafe=wsck) for wsck 
        in prof.conferenceKeysToAttend]
        conferences = ndb.get_multi(conf_keys)

        # get organizers
        organisers = [ndb.Key(Profile, conf.organizerUserId)
        for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return set of ConferenceForm objects per Conference
        return ConferenceForms(items=[self._copyConferenceToForm(conf,
         names[conf.organizerUserId]) for conf in conferences]
        )


    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
            path='conference/{websafeConferenceKey}',
            http_method='POST', name='registerForConference')
    def registerForConference(self, request):
        """Register user for selected conference."""
        return self._conferenceRegistration(request)


    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
            path='conference/{websafeConferenceKey}',
            http_method='DELETE', name='unregisterFromConference')
    def unregisterFromConference(self, request):
        """Unregister user for selected conference."""
        return self._conferenceRegistration(request, reg=False)


    @endpoints.method(message_types.VoidMessage, ConferenceForms,
            path='filterPlayground',
            http_method='GET', name='filterPlayground')
    def filterPlayground(self, request):
        """Filter Playground"""
        q = Session.query()
        time = datetime.strptime("19:00", "%H:%M").time()
        q = q.filter(Session.startTime <= time)
        q = q.filter(Session.startTime != None)
        s = []
        for sess in q:
            if(sess.typeOfSession != 'Workshop'):
                s.append(sess)

        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, "") for conf in s]
        )


api = endpoints.api_server([ConferenceApi]) # register API
