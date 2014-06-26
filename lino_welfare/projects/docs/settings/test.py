from ..settings import *
# SITE = Site(globals(), no_local=True, remote_user_header='REMOTE_USER')
SITE = Site(globals(), remote_user_header='REMOTE_USER')
DEBUG = True
SITE.appy_params.update(raiseOnError=True)
# SITE.appy_params.update(pythonWithUnoPath='/usr/bin/python3')
SITE.default_build_method = "appypdf"
SITE.webdav_url = '/'
