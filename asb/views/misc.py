import random

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config

from asb import db
import asb.forms

empty_bulletin_messages = [
    'The bulletin is empty for the time being.  Someone has arranged all the '
         'thumbtacks into a smiling {pokemon} face.',
    'The bulletin is empty for the time being... aside from a gaudy ad '
        'exclaiming "Teach Your {pokemon} to DANCE!", anyway.',
    'The bulletin is empty for the time being, except for a lonely "lost '
        '{pokemon}" poster up in the corner.  "We miss Cupcake – last seen '
        'Tuesday night – call if found!"',
    'The bulletin is empty for the time being, ignoring the six identical '
        'flyers taking advantage of the space.  "Discover this one weird '
        'trick invented by a local {pokemon} — Nurse Joys everywhere HATE '
        'her!"'
]

def empty_bulletin_message():
    """Return a silly message for when the trainer/mod bulletin is empty."""

    pokemon = (
        db.DBSession.query(db.PokemonSpecies)
        .get(random.randrange(1, 720))
    )

    return random.choice(empty_bulletin_messages).format(pokemon=pokemon.name)

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

    trainer = request.user
    stuff = {'empty_bulletin_message': empty_bulletin_message}

    if request.has_permission('account.validate', trainer):
        stuff['bulletin'] = [
            ('Your account still needs to be validated', '/validate')
        ]
    elif trainer is not None:
        bulletin = []

        # Check if any of their Pokémon need their forms chosen
        form_uncertain_pokemon = (
            db.DBSession.query(db.Pokemon)
            .filter_by(trainer_id=trainer.id, form_uncertain=True)
            .all()
        )

        for pokemon in form_uncertain_pokemon:
            bulletin.append((
                "{}'s form needs to be chosen".format(pokemon.name),
                request.resource_path(pokemon, 'edit')
            ))

        # Check if any of their bank transactions have been approved/denied
        transaction_count_base = (
            db.DBSession.query(db.BankTransaction)
            .filter_by(trainer_id=trainer.id)
            .filter_by(state='processed')
        )

        approved = transaction_count_base.filter_by(is_approved=True).count()
        denied = transaction_count_base.filter_by(is_approved=False).count()
        transactions = approved + denied

        if transactions:
            message = 'You have {n} new bank notification{s}'.format(
                n=transactions,
                s='s' if transactions > 1 else ''
            )

            if not denied:
                message += ' ({} approved)'.format(approved)
            elif not approved:
                message += ' ({} denied)'.format(denied)
            else:
                message += ' ({} approved, {} denied)'.format(approved, denied)

            bulletin.append((message, '/bank#recent'))

        stuff['bulletin'] = bulletin

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
            .filter(db.BankTransaction.trainer_id != trainer.id)
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
