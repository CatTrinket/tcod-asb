from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .db import (
    DBSession,
    Base,
    )
from .views import user
from asb.resources import get_root


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings.update(global_config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory=get_root)
    config.include('pyramid_mako')

    authn_policy = AuthTktAuthenticationPolicy(settings['secret'],
        callback=user.get_user_roles, hashalg='sha512', reissue_time=1728000,
        timeout=2592000, max_age=2592000)  # Reissue at 20 days, expire at 30
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(user.get_user, 'user', reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)

    # Add routes for one-off pages (most pages use traversal; see resources.py)
    config.add_route('home', '/')

    config.add_route('register', '/register')
    config.add_route('validate', '/validate')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('pokemon.buy', '/pokemon/buy')
    config.add_route('pokemon.buy.checkout', '/pokemon/buy/checkout')

    config.add_route('items.buy', '/items/buy')

    config.add_route('bank', '/bank')
    config.add_route('bank.approve', '/bank/approve')

    # A route to redirect away trailing slashes instead of just 404ing
    config.add_route('slash_redirect', '/{path:.+}/')

    config.scan()

    return config.make_wsgi_app()
