# Aryon

- Aryon is an RSS reader written in Python with support for authentication via OpenID Connect.

## Instructions

- To get started, clone the repo & copy `config.yaml.sample` to `config.yaml`.
  - For now, the only configurable options are the database URL, OIDC and whether the application should support multiple users.
  - OIDC can be on or off in single-user mode, but if you want multi-user support you **have to enable OIDC**. Otherwise the application has no way to distinguish users from each other.
    - If you choose to enable OIDC, you have to configure the `WELL_KNOWN_URL`, `CLIENT_ID` & `CLIENT_SECRET` according to your environment. This application is verified to work with Authentik, but should work with everything that supports OIDC - it's an open standard.

```bash
# create a virtual environment (optional)
python -m venv .venv
# activate the virtual environment (optional)
source .venv/bin/activate
# install libraries (not optional)
pip install -r requirements.txt
```

## Acknowledgments

- Implementing OIDC was **greatly** simplified by [this](https://paragraph.xyz/@digitalmeadow/%5Bpython%5D-sso-using-flask,-requests-oauthlib-and-pyjwt) wonderful article ([Github gist with the code](https://gist.github.com/gchamon/0c8632bfd32aea9a6a5a558f823e7a24))
- The OIDC implementation relies on the [`requests-oauthlib` library](https://github.com/requests/requests-oauthlib) (see article above)
  - Some more reading: [ID token](https://openid.net/specs/openid-connect-core-1_0.html#IDToken), [claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims), [authorization flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1)
- RSS feed parsing is done using the [`feedparser` library](https://github.com/kurtmckee/feedparser/).
- All SQL-related things are implemented using [SQLAlchemy](https://www.sqlalchemy.org/)
