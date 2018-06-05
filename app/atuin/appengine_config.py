# -*- coding: utf-8 -*-
"""`appengine_config` gets loaded when starting a new application instance."""
import os
import vendor

# insert `lib` as a site directory so our `main` module can load
# third-party libraries, and override built-ins with newer
# versions.
vendor.add('../lib')


def webapp_add_wsgi_middleware(app):
    import gae_mini_profiler.profiler
    app = gae_mini_profiler.profiler.ProfilerWSGIMiddleware(app)
    return app


def gae_mini_profiler_should_profile_production():
    pass
    from google.appengine.api import users
    return users.is_current_user_admin()


def gae_mini_profiler_should_profile_development():
    pass


# authentication fix for appcfg download_data and upload_data
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = (
        'REMOTE_ADDR', ['127.0.0.1'])
