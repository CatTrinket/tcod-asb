import datetime

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

from asb import db
import asb.forms

class AllowanceForm(asb.forms.CSRFTokenForm):
    """A simple form for collecting allowance."""

    collect = wtforms.SubmitField('Collect allowance')

def can_collect_allowance(trainer):
    """Return whether or not this trainer can collect allowance."""

    # If they've never collected allowance, then of course they can!
    if trainer.last_collected_allowance is None:
        return True

    # Find the most recent Friday, possibly today.  Subtracting the weekday
    # brings us back to Monday; three days further is Friday; modulo one week.
    today = datetime.date.today()
    last_friday = today - datetime.timedelta(days=(today.weekday() + 3) % 7)

    return trainer.last_collected_allowance < last_friday

@view_config(route_name='bank', request_method='GET', renderer='/bank.mako',
  permission='manage-account')
def bank(context, request):
    """The bank page."""

    if can_collect_allowance(request.user):
        allowance_form = AllowanceForm(csrf_context=request.session)
    else:
        allowance_form = None

    return {'allowance_form': allowance_form}

@view_config(route_name='bank', request_method='POST', renderer='/bank.mako',
  permission='manage-account')
def bank_process(context, request):
    """Give the trainer their allowance, if they haven't already collected it
    this week.
    """

    trainer = request.user

    if not can_collect_allowance(trainer):
        raise httpexc.HTTPForbidden(
            "You've already collected this week's allowance!")

    form = AllowanceForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'allowance_form': form}

    trainer.money += 3
    trainer.last_collected_allowance = datetime.date.today()

    return httpexc.HTTPSeeOther('/bank')
