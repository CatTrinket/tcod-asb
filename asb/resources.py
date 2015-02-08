"""Define all the resources and the traversal tree."""

import pyramid
import pyramid.httpexceptions as httpexc
import pyramid.security as sec
from sqlalchemy.orm.exc import NoResultFound

from asb import db

class Root(dict):
    """A root resource."""
    __name__ = None
    __parent__ = None

    __acl__ = [
        (sec.Allow, 'validated', 'account.manage'),
        (sec.Deny, sec.Everyone, 'account.manage'),

        (sec.Deny, 'validated', 'account.validate'),
        (sec.Allow, sec.Authenticated, 'account.validate'),
        (sec.Deny, sec.Everyone, 'account.validate'),

        (sec.Allow, 'admin', 'bank.approve'),
        (sec.Allow, 'mod', 'bank.approve'),
        (sec.Deny, sec.Everyone, 'bank.approve'),

        (sec.Allow, 'admin', 'trainer.edit'),
        (sec.Deny, sec.Everyone, 'trainer.edit'),

        (sec.Allow, 'referee', 'battle.open'),
        (sec.Deny, sec.Everyone, 'battle.open'),

        (sec.Allow, 'admin', 'flavor.edit'),
        (sec.Allow, 'mod', 'flavor.edit'),
        (sec.Deny, sec.Everyone, 'flavor.edit'),

        (sec.Deny, sec.Everyone, sec.ALL_PERMISSIONS)
    ]

class DexIndex:
    """A resource for anything in the database whose info you'd want to look
    up.
    """

    table = None
    redirect_message = None

    def __getitem__(self, identifier):
        """Get the requested resource from the database."""

        try:
            item = (db.DBSession.query(self.table)
                .filter_by(identifier=identifier)
                .one())
        except NoResultFound:
            # Attempt to redirect
            redirect = self._redirect(identifier)

            if redirect is None:
                raise KeyError
            else:
                dummy_request = pyramid.request.Request.blank('/')
                path = dummy_request.resource_path(
                    redirect.__parent__, redirect.__name__)

                return httpexc.HTTPMovedPermanently(path, self.redirect_message)
        else:
            return item

    def _redirect(self, identifier):
        """Return an object to redirect to, or None if none is applicable.

        Subclasses override this.
        """

        return None

class IDRedirectResource(DexIndex):
    """A DexIndex resource for anything whose identifier includes its ID, which
    can redirect based on the ID if the slug is bogus.
    """

    redirect_message = 'Redirected from {0} to {1}'

    def _redirect(self, identifier):
        """Attempt to redirect based on the ID."""

        id, sep, slug = identifier.partition('-')

        if not id.isnumeric():
            # No ID portion.  Haha, well, never mind then.
            return None

        id = int(id)

        # Retrieve the thing with this ID, if there is one
        try:
            item = (db.DBSession.query(self.table)
                .filter_by(id=id)
                .one())
        except NoResultFound:
            return None
        else:
            return item

class TrainerIndex(IDRedirectResource):
    __name__ = 'trainers'
    table = db.Trainer

class PokemonIndex(IDRedirectResource):
    __name__ = 'pokemon'
    table = db.Pokemon

class BattleIndex(IDRedirectResource):
    __name__ = 'battles'
    table = db.Battle

class SpeciesIndex(DexIndex):
    """Actually a form index."""

    __name__ = 'species'
    table = db.PokemonForm

    def _redirect(self, identifier):
        """Redirect to the default form if the identifier matches a species but
        not a form.
        """

        try:
            species = (db.DBSession.query(db.PokemonSpecies)
                .filter_by(identifier=identifier)
                .one())
        except NoResultFound:
            return None
        else:
            return species.default_form

class MoveIndex(DexIndex):
    __name__ = 'moves'
    table = db.Move

class AbilityIndex(DexIndex):
    __name__ = 'abilities'
    table = db.Ability

class ItemIndex(DexIndex):
    __name__ = 'items'
    table = db.Item

class TypeIndex(DexIndex):
    __name__ = 'types'
    table = db.Type

def get_root(request):
    """Get a root object."""

    root = Root({
        'trainers': TrainerIndex(),
        'pokemon': PokemonIndex(),
        'battles': BattleIndex(),
        'species': SpeciesIndex(),
        'moves': MoveIndex(),
        'abilities': AbilityIndex(),
        'items': ItemIndex(),
        'types': TypeIndex()
    })
    
    for name, index in root.items():
        index.__parent__ = root
        index.table.__parent__ = index
        index.table.__name__ = name

    return root
