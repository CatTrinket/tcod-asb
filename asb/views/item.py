import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models
from asb.resources import ItemIndex

@view_config(context=ItemIndex, renderer='/indices/items.mako')
def ItemIndex(context, request):
    """The index of all the different items."""

    items = (
        models.DBSession.query(models.Item)
        .order_by(models.Item.name)
        .all()
    )

    return {'items': items}

@view_config(context=models.Item, renderer='/item.mako')
def Item(context, request):
    """An item's dex page."""

    return {'item': context}
