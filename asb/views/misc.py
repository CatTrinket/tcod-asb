from pyramid.view import view_config

@view_config(route_name='home', renderer='/home.mako')
def home(context, request):
    # XXX is this necessary
    return {}
