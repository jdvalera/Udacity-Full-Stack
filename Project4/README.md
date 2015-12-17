Conference Central
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


### About
Conference Central is a conference organization application supported by a cloud-based API server. The API supports: user authentication, user profiles, conference information and various manners in which to query data. The front-end and base functionalities were provided by Udacity.


### Technologies used:
- [Google App Engine][1]
- [Python 2.7][2]
- [Google Cloud Endpoints][3]

## Design Choices

### Task 1: Add Sessions to a Conference

Added following endpoints:
- **getConferenceSessions**: Given a conference, return all sessions.
- **getConferenceSessionsByType**: Given a conference, 
 return all sessions of a specified type (eg lecture, keynote, workshop) **Note:** searching is case sensitive.
- **getSessionsBySpeaker**: Given a speaker, return all sessions given by this particular speaker, across all conferences
- **createSession**: Creates a session in a conference. Open only to the organizer of the conference.
- **createSpeaker**: Creates a speaker with a name, bio, and organization.
- **getSpeakers**: Return all speakers.

**The `Session` model design:**
- `name`: A required string property.
- `highlights`: Stores string of session highlights.
- `speakerKeys`: Stores multiple keys of speakers. Properties: `kind='Speaker'` `repeated=True` 
- `duration`: A string property that takes in duration of session in minutes.
- `typeOfSession`: String that stores type of session.
- `date`: A date property with format `YYYY-MM-DD`
- `startTime`: A time property in a 24-hour format. `HH:MM`

**The `SessionForm` design:**
Contains every field in the `Session` model but adds three fields: websafeConferenceKey, websafeSessionKey, speakerNames.
- `websafeConferenceKey`: Container for a web safe Conference key which helps determine which Conference a session belongs to.
- `websafeSessionKey`: Container for a web safe Session key which helps determine the targeted session.
- `speakerNames`: Displays the speaker's names based on the speaker keys.

**The `Speaker` model design:**
- `name`: A required string property.
- `bio`: A string that stores a speaker's bio.
- `organization`: A string that stores the speaker's organization.

**The `SpeakerForm` design:**
Contains all fields in `Speaker` but adds a websafeKey field.
- `websafeKey`: Container for a speaker's web safe key. Helps determine the targeted speaker.

The `Conference` and `Session` entities represent a one-to-many relationship. There can be many sessions in a conference. To create this type of a relationship I used a parent-child implementation for `Conference` and `Session`. This allows for ancestor queries which simplifies certain queries. I added a property in the `Conference` entity which returns all sessions that belong to a conference which can later be used to simplify a query.

I created a seperate entity to represent speakers. The `Session` and `Speaker` entity uses a many-to-many relationship and is not implemented using a parent-child implementation. Each session can have multiple speakers and this is done by adding a `speakerKeys` property in the `Session` entity which stores multiple `Speaker` keys and each speaker can be in multiple sessions. I also added a property in the `Speaker` entity which returns all sessions that the speaker is speaking in. Having a `Speaker` entity allows for storing information about a speaker. The drawback to this approach is that a speaker must first be registered before being able to be added to a session.

To add a speaker to a session the user must first create a speaker instance. The user then needs to retrieve the Speaker key from either the `getSpeakers` endpoint or from the admin console. If a padding error is given check whether there is a trailing or leading space when inputting keys.

### Task 2: Add Sessions to User Wishlist
I modified the `Profile` kind and added a property `sessionsKeysToAttend` to store all sessions a user is interested in attending.
Session wishlists are open to any session even if a user is not registered to a conference.

The following endpoints were added:
- **addSessionToWishlist**: adds the session to the user's list of sessions they are interested in attending.
- **getSessionsInWishlist()**: query for all the sessions in a conference that the user is interested in.
- **deleteSessionInWishlist**: removes the session from the user's list of sessions they are interested in attending

### Task 3: Indexes and Queries
**Additional Queries:**
- `getSessionsByPopularity`: Given a web safe Conference key return all sessions by wishlist popularity. This allows users to see which sessions are most popular so they can better plan their schedule.
- `showSpeakerInfo`: Return info on the speakers speaking in a Session given a web safe Session key. This allows users to have some background information on speakers speaking at a session.

**Query related problem:**
> Let’s say that you don't like workshops and you don't like sessions after 7 pm. How would you handle a query for all non-workshop sessions before 7 pm? What is the problem for implementing this query? What ways to solve it did you think of?

**Solution:**
Since Ndb only supports one inequality filter per property I used a query for sessions before 7 pm. After fetching the results from the query I used Python to filter out any sessions that were of type 'workshop'. This query is implemented with the endpoint `getNonWorkshopBeforeSeven` which returns all non-workshop sessions before 7 pm across all conferences.

### Task 4: Add Featured Speaker using a Task
The `createSession` endpoint was modified to add a task to the queue if one ore more speakers are passed to the endpoint. The task is handled in `main.py` with `SetFeaturedSpeakerHandler` which calls on `_cacheFeaturedSpeaker`. The task checks if the speaker has two or more sessions in a conference and if the speaker has more than one session in the conference make that speaker the featured speaker. If more than one speaker is passed to the `createSession` endpoint the featured speaker will be determined by which speaker has more sessions in the conference. Memcache is used by the task to store information on the featured speaker. The endpoint `getFeaturedSpeaker` returns the featured speaker and some information using the memcache.


## Setup Instructions
Download and install [Google App Engine SDK for Python][7] if not already installed.
Once installed:

1. Clone the repository. `Project 4` directory is the only directory needed for this application.
2. After cloning the repository go to Google at https://console.developers.google.com and configure your OAuth credentials.
3. Once you have obtained your client id, update `WEB_CLIENT_ID` in `settings.py` and `CLIENT_ID` in `/static/js/app.js`.
4. Update `application` in `app.yaml` with your App Engine project name.
5. Run the project locally using Google App Engine Launcher. The server's address is [localhost:8080][5] by default.
6. Deploy application.

## Resources


[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool
[7]: https://cloud.google.com/appengine/downloads

