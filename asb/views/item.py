import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models

@view_config(route_name='item_index', renderer='/indices/items.mako')
def ItemIndex(context, request):
    """The index of all the different items."""

    items = (
        models.DBSession.query(models.Item)
        .order_by(models.Item.name)
        .all()
    )

    return {'items': items}

@view_config(route_name='item', renderer='/item.mako')
def Item(context, request):
    """An item's dex page."""

    try:
        item = (
            models.DBSession.query(models.Item)
            .filter_by(identifier=request.matchdict['identifier'])
            .one()
        )
    except NoResultFound:
        raise httpexc.HTTPNotFound

    return {'item': item}
