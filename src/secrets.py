"""Contains various non-public strings."""


class db:

  auto = ('{SECRET_DB_USERNAME_AUTO}', '{SECRET_DB_PASSWORD_AUTO}')
  backup = ('{SECRET_DB_USERNAME_BACKUP}', '{SECRET_DB_PASSWORD_BACKUP}')
  epi = ('{SECRET_DB_USERNAME_EPI}', '{SECRET_DB_PASSWORD_EPI}')


class api:

  twitter = '{SECRET_API_AUTH_TWITTER}'
  ght = '{SECRET_API_AUTH_GHT}'
  fluview = '{SECRET_API_AUTH_FLUVIEW}'
  cdc = '{SECRET_API_AUTH_CDC}'
  quidel = '{SECRET_API_AUTH_QUIDEL}'
  quidel = '{SECRET_API_AUTH_NOROSTAT}'
  sensors = '{SECRET_API_AUTH_SENSORS}'


class flucontest:

  debug_userid = '{SECRET_FLUCONTEST_DEBUG_USERID}'
  email_maintainer = '{SECRET_FLUCONTEST_EMAIL_MAINTAINER}'
  email_delphi = '{SECRET_FLUCONTEST_EMAIL_DELPHI}'
  email_cdc = '{SECRET_FLUCONTEST_EMAIL_CDC}'
  email_epicast = '{SECRET_FLUCONTEST_EMAIL_EPICAST}'
  flusight = ('{SECRET_FLUCONTEST_FLUSIGHT_EMAIL}', '{SECRET_FLUCONTEST_FLUSIGHT_PASSWORD}')


class healthtweets:

  login = ('{SECRET_HEALTHTWEETS_USERNAME}', '{SECRET_HEALTHTWEETS_PASSWORD}')


class googletrends:

  apikey = '{SECRET_GOOGLE_TRENDS_API_KEY}'


class wiki:

  hmac = '{SECRET_WIKI_HMAC}'


class cdcp:

  dropbox_token = '{SECRET_CDCP_DROPBOX_TOKEN}'


class mailgun:

  key = '{SECRET_MAILGUN_AUTH_KEY}'


class apache:

  keys_dir = '{SECRET_APACHE_KEYS_DIR}'


class quidel:

  email_addr = '{SECRET_QUIDEL_EMAIL_ID}'
  email_pwd = '{SECRET_QUIDEL_EMAIL_PWD}'
