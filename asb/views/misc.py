import pyramid.httpexceptions as httpexc
from pyramid.view import view_config

@view_config(context=Exception, renderer='/error.mako')
def error(error, request):
    """Return a generic error page for an arbitrary uncaught exception."""

    request.response.status_int = 500

    return {'status': '500 Internal Server Error', 'message': None}

@view_config(context=httpexc.HTTPError, renderer='/error.mako')
def error_specific(error, request):
    """Return a more helpful error page for an uncaught HTTPError."""

    request.response.status_int = error.code

    return {
        'status': '{} {}'.format(error.code, error.title),
        'message': '{}  (Detail: {})'.format(error.explanation, error.detail)
    }

@view_config(route_name='home', renderer='/home.mako')
def home(context, request):
    # XXX is this necessary
    return {}
