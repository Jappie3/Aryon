# Aryon

- Aryon is an RSS reader written in Python with support for authentication via OpenID Connect.

> Disclaimer: this application was made by a student as a school project. Run this code at your own risk.

## Instructions

- To get started, clone the repo & copy `config.yaml.sample` to `config.yaml`.
  - For now, the only configurable options are the database URL, OIDC and whether the application should support multiple users.
  - OIDC can be on or off in single-user mode, but if you want multi-user support you **have to enable OIDC**. Otherwise the application has no way to distinguish users from each other.
    - If you choose to enable OIDC, you have to configure the `WELL_KNOWN_URL`, `CLIENT_ID` & `CLIENT_SECRET` according to your environment. This application is verified to work with Authentik, but should work with everything that supports OIDC - it's an open standard.
- Steps to run the application:

```bash
# create a virtual environment (optional)
python -m venv .venv
# activate the virtual environment (optional)
source .venv/bin/activate
# install libraries (not optional)
pip install -r requirements.txt
```

- There is also a Docker compose file in case you want to containerize this application
    - Make sure to copy `config.yaml.sample` to `config.yaml` (and change it according to your use case) before running `docker compose up -d`
    - Note about ownership of the files: every time the container runs, the ownership of the `/app` directory (to which the `/src` directory on the host is mapped) will get changed to `2002:2002`
        - If you want to modify the config either:
            - Edit the file as root
            - Change the ownership so that your user can edit it (requires `sudo`, `doas`, etc.). When (re)starting the container, the **ownership will get set to `2002:2002` again**.
        - Why is this? I don't run the application as root, but as a user with UID 2002. If the ownership is not set correctly, the program will not be able to access the config file.
- Here are some RSS feeds you can test with (I am not affiliated with these feeds nor with the contents of them):
    - https://theorangeone.net/posts/feed/
    - https://www.vrt.be/vrtnws/en.rss.articles.xml

## Acknowledgments

- Implementing OIDC was **greatly** simplified by [this](https://paragraph.xyz/@digitalmeadow/%5Bpython%5D-sso-using-flask,-requests-oauthlib-and-pyjwt) wonderful article ([Github gist with the code](https://gist.github.com/gchamon/0c8632bfd32aea9a6a5a558f823e7a24))
- The OIDC implementation relies on the [`requests-oauthlib` library](https://github.com/requests/requests-oauthlib) (see article above)
  - Some more reading: [ID token](https://openid.net/specs/openid-connect-core-1_0.html#IDToken), [claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims), [authorization flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1)
- RSS feed parsing is done using the [`feedparser` library](https://github.com/kurtmckee/feedparser/).
- All SQL-related things are implemented using [SQLAlchemy](https://www.sqlalchemy.org/)
