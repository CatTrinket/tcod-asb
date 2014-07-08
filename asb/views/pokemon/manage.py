import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

from asb import db
import asb.forms
from asb.resources import PokemonIndex

class PokemonMovingForm(asb.forms.CSRFTokenForm):
    """A form for selecting Pokémon to deposit or withdraw.

    Several parts of this form must be created dynamically, using
    pokemon_deposit_form or pokemon_withdraw_form (below).
    """

    pokemon = asb.forms.MultiCheckboxField(coerce=int)
    submit = wtforms.SubmitField()


def pokemon_deposit_form(trainer, request, use_post=True):
    """Return a PokemonMovingForm for depositing Pokémon."""

    post = request.POST if use_post else None
    form = PokemonMovingForm(post, csrf_context=request.session)

    form.pokemon.choices = [(p.id, '') for p in trainer.squad]

    # The Length validator is intended for strings, but this works so whatever
    form.pokemon.validators.append(
        wtforms.validators.Length(max=len(trainer.squad) - 1,
            message='You must keep at least one Pokémon in your active squad')
    )

    form.submit.label = wtforms.fields.Label('submit', 'Deposit')

    return form

def pokemon_withdraw_form(trainer, request, use_post=True):
    """Return a PokemonMovingForm for withdrawing Pokémon."""

    post = request.POST if use_post else None
    form = PokemonMovingForm(post, csrf_context=request.session)

    form.pokemon.choices = [(p.id, '') for p in trainer.pc]

    if form.pokemon.data:
        # We want to tell them how many Pokémon they're over by if they try to
        # withdraw too many, which means we have to add this validator when the
        # form is being submitted.  Thankfully, that's exactly when we need it.
        max_withdraws = 10 - len(trainer.squad)
        overflow = len(form.pokemon.data) - max_withdraws

        if max_withdraws == 0:
            message = 'Your squad is full!'
        else:
            message = ('You only have room in your squad to withdraw {0} more '
                'Pokémon; please uncheck at least {1}'.format(max_withdraws,
                overflow))

        form.pokemon.validators.append(wtforms.validators.Length(
            max=max_withdraws, message=message))

    form.submit.label = wtforms.fields.Label('submit', 'Withdraw')

    return form

@view_config(name='manage', context=PokemonIndex, permission='account.manage',
  request_method='GET', renderer='/manage/pokemon.mako')
def manage_pokemon(context, request):
    """A page for depositing and withdrawing one's Pokémon."""

    trainer = request.user

    if trainer.squad:
        deposit = pokemon_deposit_form(trainer, request)
    else:
        deposit = None

    if trainer.pc:
        withdraw = pokemon_withdraw_form(trainer, request)
    else:
        withdraw = None

    return {'trainer': trainer, 'deposit': deposit, 'withdraw': withdraw}

@view_config(name='manage', context=PokemonIndex, permission='account.manage',
  request_method='POST', renderer='/manage/pokemon.mako')
def manage_pokemon_commit(context, request):
    """Process a request to deposit or withdraw Pokémon."""

    trainer = request.user

    if request.POST['submit'] == 'Deposit':
        deposit = pokemon_deposit_form(trainer, request)
        withdraw = pokemon_withdraw_form(trainer, request, use_post=False)
        form = deposit
        is_in_squad = False
    elif request.POST['submit'] == 'Withdraw':
        deposit = pokemon_deposit_form(trainer, request, use_post=False)
        withdraw = pokemon_withdraw_form(trainer, request)
        form = withdraw
        is_in_squad = True

    if not form.validate():
        return {'trainer': trainer, 'deposit': deposit, 'withdraw': withdraw}

    to_toggle = (db.DBSession.query(db.Pokemon)
        .filter(db.Pokemon.id.in_(form.pokemon.data))
        .all())

    for pokemon in to_toggle:
        pokemon.is_in_squad = is_in_squad

    return httpexc.HTTPSeeOther('/pokemon/manage')
