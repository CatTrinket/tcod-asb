from pyramid.view import view_config

@view_config(route_name='home', renderer='/home.mako')
def TrainerIndex(context, request):
    return {}
