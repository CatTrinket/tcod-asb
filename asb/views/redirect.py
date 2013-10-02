import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models

def attempt_redirect(bogus_identifier, table, request):
    id, _, slug = bogus_identifier.partition('-')

    if id.isnumeric():
        id = int(id)
        try:
            identifier, = (
                models.DBSession.query(table.identifier)
                .filter_by(id=id).one()
            )
        except NoResultFound:
            raise httpexc.HTTPNotFound()

        raise httpexc.HTTPMovedPermanently(
            request.current_route_path(identifier=identifier))
    else:
        raise httpexc.HTTPNotFound()

@view_config(route_name='slash_redirect')
def slash_redirect(context, request):
    """Redirect away erroneous trailing slashes."""
    raise httpexc.HTTPMovedPermanently(request.path.rstrip('/'))
