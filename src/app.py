from urllib.parse import unquote
from uuid import uuid4

import feedparser
import jwt
import requests
from dateutil import parser
from flask import Flask, render_template, request, redirect, session, url_for
from jwt import PyJWKClient
from jwt.exceptions import DecodeError
from requests_oauthlib import OAuth2Session
from werkzeug.exceptions import InternalServerError, Unauthorized

from util.config import config
from util.get_from_db import *

# TODO
# logout route & button
# unread indicator
# feed groups
# should I keep usernames? (defaults to empty string rn) or just use the sub from the token & the id from the db
# refresh the feeds: automatically or only on-demand?
# database conversion between single- and multi-user mode (basically just give the single user an OIDC sub)


app = Flask(__name__, static_folder="templates/static")

app.config['SECRET_KEY'] = str(uuid4())
IDP_CONFIG = {}
try:
    if config["OIDC_ENABLED"]:
        IDP_CONFIG = {
            "well_known_url": config["OIDC_WELL_KNOWN_URL"],
            "client_id": config["OIDC_CLIENT_ID"],
            "client_secret": config["OIDC_CLIENT_SECRET"],
            "scope": config["OIDC_SCOPE"],
        }
except KeyError as e:
    raise InternalServerError(f"Missing configuration: {e}")


def get_well_known_metadata():
    response = requests.get(IDP_CONFIG["well_known_url"])
    response.raise_for_status()
    return response.json()


def get_oauth2_session(**kwargs):
    oauth2_session = OAuth2Session(IDP_CONFIG["client_id"],
                                   scope=IDP_CONFIG["scope"],
                                   redirect_uri=url_for(".callback", _external=True),
                                   **kwargs)
    return oauth2_session


def get_jwks_client():
    well_known_metadata = get_well_known_metadata()
    return PyJWKClient(well_known_metadata["jwks_uri"])


jwks_client = None
if config["OIDC_ENABLED"]:
    jwks_client = get_jwks_client()


@app.before_request
def verify_and_decode_token():
    """
    Verify and decode the JWT token before each request (except /login and /callback)
    :return: None
    """
    if request.endpoint not in {"login", "callback"} and config["OIDC_ENABLED"]:
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split()[1]
        elif "oauth_token" in session:
            token = session["oauth_token"]
        else:
            # return Unauthorized("Missing authorization token")
            # if not logged in -> redirect to /login
            return redirect("/login")

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            header_data = jwt.get_unverified_header(token)
            request.user_data = jwt.decode(token,
                                           signing_key.key,
                                           algorithms=[header_data['alg']],
                                           audience=IDP_CONFIG["client_id"])
        except DecodeError:
            return Unauthorized("Authorization token is invalid")
        except Exception as e:
            print(e)
            return InternalServerError("Error authenticating client")


@app.route("/login")
def login():
    """
    Redirect the user to the IDP for login
    :return: redirect
    """
    well_known_metadata = get_well_known_metadata()
    oauth2_session = get_oauth2_session()
    authorization_url, state = oauth2_session.authorization_url(well_known_metadata["authorization_endpoint"])
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    """
    Callback from the IDP
    :return: redirect to / if successful
    """
    well_known_metadata = get_well_known_metadata()
    oauth2_session = get_oauth2_session(state=session["oauth_state"])
    session["oauth_token"] = oauth2_session.fetch_token(well_known_metadata["token_endpoint"],
                                                        client_secret=IDP_CONFIG["client_secret"],
                                                        code=request.args["code"])["id_token"]
    # return "ok"
    return redirect("/")


@app.route("/user/token")
def get_user_token():
    if not config["OIDC_ENABLED"]:
        return "single_user"
    return session["oauth_token"]


@app.route("/user/id")
def get_user_id():
    if not config["OIDC_ENABLED"]:
        return "single_user"
    return request.user_data["sub"]


@app.route("/")
def index():
    """
    Render the index page
    :return: rendered template
    """
    if not config["OIDC_ENABLED"]:
        # if OIDC is disabled, use single_user
        with db_session() as dbsession:
            oidc_sub = "single_user"
            if not dbsession.query(User).filter_by(oidc_sub=oidc_sub).first():
                # print("adding user")
                user = User(oidc_sub=oidc_sub)
                dbsession.add(user)
                dbsession.commit()
            # else:
            # print("user exists")
    else:
        # check if user exists in database, if not, add them
        with db_session() as dbsession:
            oidc_sub = request.user_data["sub"]
            if not dbsession.query(User).filter_by(oidc_sub=oidc_sub).first():
                # print("adding user")
                user = User(oidc_sub=oidc_sub)
                dbsession.add(user)
                dbsession.commit()
            # else:
            # print("user exists")
    return render_template("index.html", feeds=get_feeds())


@app.route("/feed/<feed_id>")
def feed(feed_id):
    """
    Render the page for a given feed
    :param feed_id: ID of the feed to render
    :return: rendered template
    """
    return render_template("index.html", feeds=get_feeds(), articles=get_articles(feed_id))


@app.route("/add_feed", methods=['POST'])
def add_feed():
    """
    Add a new feed to the database
    """
    feed_url = unquote(request.form['url'])
    feed_title = unquote(request.form['title'])
    new_feed = RssFeed(title=feed_title, url=feed_url)
    with db_session() as dbsession:
        try:
            dbsession.add(new_feed)
            dbsession.commit()
        except Exception as e:
            print(e)
            dbsession.rollback()
            raise
        print(f"Added feed {new_feed.title} ({new_feed.url}) to database")
        # todo should this functionality go elsewhere?
        # add articles for the new feed to the database
        feed_articles = feedparser.parse(feed_url).entries
        articles = []
        for feed_article in feed_articles:
            published_date = parser.parse(feed_article.published)
            articles.append(FeedArticle(feed_id=new_feed.id, title=feed_article.title, url=feed_article.link,
                                        summary=feed_article.summary, date=published_date))
    with db_session() as dbsession:
        try:
            dbsession.add_all(articles)
            dbsession.commit()
        except Exception as e:
            print(e)
            dbsession.rollback()
            raise
        print(f"Added {len(articles)} articles to database")
    return render_template("index.html", feeds=get_feeds())


def refresh_feeds(user_id=0):
    # default user_id to 0, meaning refresh all feeds
    # todo refresh feeds
    pass


def check_config():
    """
    Check the config file for any errors or inconsistencies
    """
    is_multiuser = config["IS_MULTIUSER"]
    oidc_enabled = config["OIDC_ENABLED"]
    # check user mode & oidc settings
    match (is_multiuser, oidc_enabled):
        case (False, False):
            print("Starting application in single-user mode without OIDC.")
        case (False, True):
            print("Starting application in single-user mode with OIDC enabled.")
        case (True, True):
            print("Starting application in multi-user mode with OIDC enabled.")
        case (True, False):
            print("If you want to enable multi-user mode, also enable OpenIdConnect for identification & "
                  "authentication (OIDC_ENABLED=true in config.yaml). Otherwise there is no way to differentiate"
                  " between the different users.")
            exit(1)
        case (_, _):
            print("Something went wrong while loading the configuration file. Please check the config.yaml file.")
            exit(1)


def main():
    check_config()
    # app.run(debug=True)
    app.run()


if __name__ == "__main__":
    main()
