from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_mako')

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('pokemon_index', '/pokemon')
    config.add_route('pokemon_species_index', '/pokemon/species')
    config.add_route('pokemon', '/pokemon/{identifier}')
    config.add_route('pokemon_species', '/pokemon/species/{identifier}')

    config.add_route('trainer_index', '/trainers')
    config.add_route('trainer', '/trainers/{identifier}')

    config.add_route('register', '/register')
    config.add_route('register_done', '/register/done')
    config.add_route('login', '/login')

    config.add_route('slash_redirect', '/{path:.+}/')

    config.scan()

    return config.make_wsgi_app()
