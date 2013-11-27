import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models

@view_config(route_name='move_index', renderer='/indices/moves.mako')
def MoveIndex(context, request):
    """The index of all the moves."""

    moves = (
        models.DBSession.query(models.Move)
        .order_by(models.Move.name)
        .all()
    )

    return {'moves': moves}

@view_config(route_name='move', renderer='/move.mako')
def Move(context, request):
    """A move's dex page."""

    try:
        move = (
            models.DBSession.query(models.Move)
            .filter_by(identifier=request.matchdict['identifier'])
            .one()
        )
    except NoResultFound:
        raise httpexc.HTTPNotFound

    return {'move': move}
