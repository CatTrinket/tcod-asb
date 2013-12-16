import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models

@view_config(context=httpexc.HTTPMovedPermanently)
def redirect(context, request):
    """Catch a redirect and add a flash message based on the redirect
    exception's message.

    n.b. If a view returns an HTTPMovedPermanently rather than raising it, this
    view won't catch it.
    """

    old_path = request.path
    new_path = context.location

    if context.detail is not None:
        request.session.flash(context.detail.format(old_path, new_path))

    return context

@view_config(route_name='slash_redirect')
def slash_redirect(context, request):
    """Redirect away erroneous trailing slashes."""

    return httpexc.HTTPMovedPermanently(request.path.rstrip('/'))
