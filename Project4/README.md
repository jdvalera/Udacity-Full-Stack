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

## Setup Instructions
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

