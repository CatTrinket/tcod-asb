from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )
from .views import user


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_mako')

    authn_policy = AuthTktAuthenticationPolicy(settings['secret'],
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(user.get_user, 'user', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('pokemon_index', '/pokemon')
    config.add_route('pokemon_species_index', '/pokemon/species')
    config.add_route('pokemon', '/pokemon/{identifier}')
    config.add_route('pokemon_species', '/pokemon/species/{identifier}')

    config.add_route('trainer_index', '/trainers')
    config.add_route('trainer', '/trainers/{identifier}')

    config.add_route('item_index', '/items')
    config.add_route('item', '/items/{identifier}')

    config.add_route('move_index', '/moves')
    config.add_route('move', '/moves/{identifier}')

    config.add_route('register', '/register')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('slash_redirect', '/{path:.+}/')

    config.scan()

    return config.make_wsgi_app()
