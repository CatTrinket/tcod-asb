import datetime
import itertools

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

from asb import db
import asb.forms
import asb.tcodf


class AllowanceForm(asb.forms.CSRFTokenForm):
    """A simple form for collecting allowance."""

    collect_allowance = wtforms.SubmitField('Collect allowance')

class TransactionForm(wtforms.Form):
    """A single bank transaction."""

    amount = wtforms.IntegerField()
    link = asb.forms.PostLinkField()

    def validate(self):
        """Validate, unless all fields are empty."""

        if any(any(data.strip() for data in field.raw_data) for field in self):
            return super(wtforms.Form, self).validate()

        return True

class DepositForm(asb.forms.CSRFTokenForm):
    """A form for depositing (or withdrawing) money."""

    transactions = wtforms.FieldList(
        wtforms.FormField(TransactionForm, [wtforms.validators.optional()]),
        min_entries=5
    )
    add_rows = wtforms.SubmitField('+')
    deposit = wtforms.SubmitField('Submit')

class TransactionClearForm(asb.forms.CSRFTokenForm):
    """A one-button form for clearing the "recent transactions" view."""

    clear = wtforms.SubmitField('Clear non-pending transactions')

class ApprovalForm(asb.forms.CSRFTokenForm):
    """A form for approving and denying bank transactions.

    Transactions must be added manually using the approval_form method below.
    """

    submit = wtforms.SubmitField('Submit')

class ApprovalTransactionForm(wtforms.Form):
    """A single transaction in an ApprovalForm."""

    what_do = wtforms.RadioField(choices=[
        ('ignore', None),
        ('approve', None),
        ('deny', None)
    ], default='ignore')

    reason = wtforms.TextField()

    def validate_reason(form, field):
        """Require a reason when denying a transaction."""

        if form.what_do.data == 'deny' and not field.data.strip():
            raise wtforms.validators.ValidationError('Please give a reason '
                'for denying this transaction.')

def approval_form(user, *args, **kwargs):
    """Create and return an approval form."""

    # Get all pending transactions, except for the approver's own
    transactions = (
        db.DBSession.query(db.BankTransaction)
        .filter_by(state='pending')
        .filter(db.BankTransaction.trainer_id != user.id)
        .order_by(db.BankTransaction.id)
        .all()
    )

    # Make form
    class Subform(wtforms.Form):
        """A subform to hold all the transaction sub-subforms."""

        pass

    for transaction_ in transactions:
        class Subsubform(ApprovalTransactionForm):
            """An ApprovalTransactionForm that also holds the transaction."""

            transaction = transaction_

        setattr(Subform, 'transaction-{0}'.format(transaction_.id),
            wtforms.FormField(Subsubform))

    class Form(ApprovalForm):
        transactions = wtforms.FormField(Subform)

    return Form(*args, **kwargs)

def can_collect_allowance(trainer):
    """Return whether or not this trainer can collect allowance."""

    # If they've never collected allowance, then of course they can!
    if trainer.last_collected_allowance is None:
        return True

    # Find the most recent Friday, possibly today.  Subtracting the weekday
    # brings us back to Monday; three days further is Friday; modulo one week.
    today = datetime.datetime.utcnow().date()
    last_friday = today - datetime.timedelta(days=(today.weekday() + 3) % 7)

    return trainer.last_collected_allowance < last_friday

def recent_transactions(trainer):
    """Get a trainer's pending, recently-approved, and recently-denied
    transactions.
    """

    base = (
        db.DBSession.query(db.BankTransaction)
        .filter(db.BankTransaction.trainer_id == trainer.id)
    )

    pending = base.filter_by(state='pending').all()
    processed = base.filter_by(state='processed')
    approved = processed.filter(db.BankTransaction.is_approved == True).all()
    denied = processed.filter(db.BankTransaction.is_approved == False).all()

    transactions = {
        'pending': pending,
        'approved': approved,
        'denied': denied
    }

    return transactions

@view_config(route_name='bank', request_method='GET', renderer='/bank.mako',
  permission='account.manage')
def bank(context, request):
    """The bank page."""

    stuff = {
        'allowance_form': None,
        'deposit_form': DepositForm(csrf_context=request.session),
        'clear_form': None
    }

    if can_collect_allowance(request.user):
        stuff['allowance_form'] = AllowanceForm(csrf_context=request.session)

    # Get recent transactions
    transactions = recent_transactions(request.user)
    stuff['recent_transactions'] = transactions

    if transactions['approved'] or transactions['denied']:
        stuff['clear_form'] = (
            TransactionClearForm(csrf_context=request.session)
        )

    return stuff

@view_config(route_name='bank', request_method='POST', renderer='/bank.mako',
  permission='account.manage')
def bank_process(context, request):
    """Give the trainer their allowance, if they haven't already collected it
    this week.
    """

    trainer = request.user

    if can_collect_allowance(request.user):
        allowance_form = AllowanceForm(request.POST,
            csrf_context=request.session)
    else:
        allowance_form = None

    deposit_form = DepositForm(request.POST, csrf_context=request.session)

    transactions = recent_transactions(trainer)
    clear_form = TransactionClearForm(request.POST,
        csrf_context=request.session)

    stuff = {'allowance_form': allowance_form, 'deposit_form': deposit_form,
        'recent_transactions': transactions, 'clear_form': clear_form}

    if allowance_form is not None and allowance_form.collect_allowance.data:
        # Make sure everything's in order
        if not can_collect_allowance(trainer):
            raise httpexc.HTTPForbidden(
                "You've already collected this week's allowance!")

        if not allowance_form.validate():
            return stuff

        # Give the trainer their allowance
        trainer.money += 3
        trainer.last_collected_allowance = datetime.datetime.utcnow().date()

        return httpexc.HTTPSeeOther('/bank')
    elif deposit_form.add_rows.data:
        # Add five rows to the deposit form
        for n in range(5):
            deposit_form.transactions.append_entry()

        return stuff
    elif deposit_form.deposit.data:
        # Add the transactions
        if not deposit_form.validate():
            return stuff

        for transaction in deposit_form.transactions:
            if transaction.amount.data:
                db.DBSession.add(db.BankTransaction(
                    trainer_id=trainer.id,
                    amount=transaction.amount.data,
                    tcod_post_id=transaction.link.post_id
                ))

        request.session.flash("Success!  You'll receive your money as soon as "
            "an ASB mod verifies and approves your transaction.")

        return httpexc.HTTPSeeOther('/bank')
    elif clear_form.clear.data:
        # Mark the user's processed transactions as acknowledged
        for transaction in itertools.chain(transactions['approved'],
          transactions['denied']):
            transaction.state = 'acknowledged'

        return httpexc.HTTPSeeOther('/bank')

    # Fallback
    return stuff

@view_config(route_name='bank.approve', request_method='GET',
  renderer='/bank_approve.mako', permission='bank.approve')
def bank_approve(context, request):
    """The bank approving page."""

    return {'form': approval_form(request.user, csrf_context=request.session)}

@view_config(route_name='bank.approve', request_method='POST',
  renderer='/bank_approve.mako', permission='bank.approve')
def bank_approve_process(context, request):
    """Process the bank approval form."""

    approver = request.user

    form = approval_form(request.user, request.POST,
        csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    for field in form.transactions:
        transaction = field.transaction

        if field.what_do.data == 'approve':
            transaction.trainer.money += transaction.amount
            transaction.state = 'processed'
            transaction.is_approved = True
            transaction.approver_id = approver.id
        elif field.what_do.data == 'deny':
            transaction.state = 'processed'
            transaction.is_approved = False
            transaction.approver_id = approver.id

            if field.reason.data:
                transaction.reason = field.reason.data

    return httpexc.HTTPSeeOther('/bank/approve')
