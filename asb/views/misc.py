import pyramid.httpexceptions as httpexc
from pyramid.view import view_config

from asb import db
import asb.forms

@view_config(context=Exception, renderer='/error.mako')
def error(error, request):
    """Return a generic error page for an arbitrary uncaught exception."""

    request.response.status_int = 500

    return {'status': '500 Internal Server Error', 'message': None}

@view_config(context=httpexc.HTTPError, renderer='/error.mako')
def error_specific(error, request):
    """Return a more helpful error page for an uncaught HTTPError."""

    request.response.status_int = error.code

    return {
        'status': '{} {}'.format(error.code, error.title),
        'message': '{}  (Detail: {})'.format(error.explanation, error.detail)
    }

@view_config(route_name='home', renderer='/home.mako')
def home(context, request):
    """The home page."""

    stuff = {}

    # Find stuff to display on the Mod Bulletin, if applicable
    if any(role in ['mod', 'admin'] for role in request.effective_principals):
        # For now, we'll just assume that the only way the user has any mod
        # permissions is if they're a mod, so we don't need to check individual
        # permissions

        mod_stuff = []

        # See if there are any pending bank transactions
        pending_transactions = (
            db.DBSession.query(db.BankTransaction)
            .filter_by(state='pending')
            .filter(db.BankTransaction.trainer_id != request.user.id)
            .count()
        )

        if pending_transactions:
            if pending_transactions == 1:
                message = 'There is 1 pending bank transaction to approve'
            else:
                message = ('There are {} pending bank transactions to approve'
                    .format(pending_transactions))

            mod_stuff.append((message, '/bank/approve'))

        stuff['mod_stuff'] = mod_stuff

    return stuff
