import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models

def attempt_redirect(bogus_identifier, table, request):
    """When someone requests a path including an invalid identifier, assume the
    ID portion is right and the name slug is wrong, and attempt to redirect to
    the correct slug.
    """

    id, _, slug = bogus_identifier.partition('-')

    if id.isnumeric():
        id = int(id)
        try:
            # Try to get the right identifier
            identifier, = (
                models.DBSession.query(table.identifier)
                .filter_by(id=id).one()
            )
        except NoResultFound:
            # The ID doesn't correspond to anything; 404 after all
            raise httpexc.HTTPNotFound()

        # Redirect
        raise httpexc.HTTPMovedPermanently(
            request.current_route_path(identifier=identifier))
    else:
        # Well, we don't even *have* an integer ID here, so never mind
        raise httpexc.HTTPNotFound()

@view_config(route_name='slash_redirect')
def slash_redirect(context, request):
    """Redirect away erroneous trailing slashes."""

    raise httpexc.HTTPMovedPermanently(request.path.rstrip('/'))
