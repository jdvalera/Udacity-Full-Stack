Conference Central
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


### About
Conference Central is a conference organization application supported by a cloud-based API server. The API supports: user authentication, user profiles, conference information and various manners in which to query data.


### Frameworks/Libraries/Technologies used:
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

**The `Session` model design:**
- `name`: A required string property.
- `highlights`: Stores string of session highlights.
- `speakerKeys`: Stores multiple keys of speakers. Properties: `kind='Speaker'` `repeated=True` 
- `duration`: A string property that takes in duration of session in minutes.
- `typeOfSession`: String that stores type of session.
- `date`: A date property with format `YYYY-MM-DD`
- `startTime`: A time property in a 24-hour format. `HH:MM`

**`SessionForm` design:**
Contains every field in the `Session` model but adds three fields: websafeConferenceKey, websafeSessionKey, speakerNames.
- `websafeConferenceKey`: Container for a web safe Conference key which helps determine which Conference a session belongs to.
- `websafeSessionKey`: Container for a web safe Session key which helps determine the targeted session.
- `speakerNames`: Displays the speaker's names based on the speaker keys.

**The `Speaker` model design:**
- `name`: A required string property.
- `bio`: A string that stores a speaker's bio.
- `organization`: A string that stores the speaker's organization.

**`SpeakerForm` design:**
Contains all fields in `Speaker` but adds a websafeKey field.
- `websafeKey`: Container for a speaker's web safe key. Helps determine the targeted speaker.




### Setup Instructions
Download and install [Google App Engine SDK for Python][7] if not already installed.
Once installed:

1. Clone the repository. `Project 4` directory is the only directory needed for this application.
2. After cloning the repository go to Google at https://console.developers.google.com and configure your OAuth credentials.
3. Once you have obtained your client id, update `WEB_CLIENT_ID` in `settings.py` and `CLIENT_ID` in `/static/js/app.js`.
4. Update `application` in `app.yaml` with your App Engine project name.
5. Run the project locally using Google App Engine Launcher. The server's address is [localhost:8080][5] by default.
6. Deploy application.


[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool
[7]: https://cloud.google.com/appengine/downloads

