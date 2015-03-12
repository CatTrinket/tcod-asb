import collections
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

    amount = wtforms.IntegerField(
        validators=[wtforms.validators.NumberRange(min=1, message='$1 minimum')]
    )
    link = asb.forms.PostLinkField()
    notes = wtforms.StringField(
        filters=[lambda note: note if note is None else note.strip()]
    )

    def validate(self):
        """Validate, unless all fields are empty."""

        if any(any(data.strip() for data in field.raw_data) for field in self):
            return super(wtforms.Form, self).validate()

        return True

class DepositForm(asb.forms.CSRFTokenForm):
    """A form for depositing money."""

    transactions = wtforms.FieldList(
        wtforms.FormField(TransactionForm, [wtforms.validators.Optional()]),
        min_entries=5
    )

    resubmitted = wtforms.HiddenField()
    add_rows = wtforms.SubmitField('+')
    deposit = wtforms.SubmitField('Submit')

    def check_for_dupes(self, request):
        """Check for posts that have been claimed multiple times, or that have
        been claimed in the past.
        """

        no_dupes = True

        # Count duplicate submissions
        post_ids = collections.Counter(
            transaction.link.post_id for transaction in self.transactions
            if transaction.link.post_id is not None
        )

        # Find past transactions for the same posts
        past_transactions = (
            db.DBSession.query(db.BankTransaction)
            .filter_by(trainer_id=request.user.id)
            .filter(db.BankTransaction.tcod_post_id.in_(post_ids))
            .all()
        )

        past_transaction_dict = {}
        for transaction in past_transactions:
            ts = past_transaction_dict.setdefault(transaction.tcod_post_id, [])
            ts.append(transaction)

        # Handle resubmitted ids
        if self.resubmitted.data:
            resubmitted_ids = map(int, self.resubmitted.data.split(','))
        else:
            # ''.split(',') == ['']
            resubmitted_ids = []

        to_resubmit = []

        # Go through and add appropriate error messages
        for transaction in self.transactions:
            id = transaction.link.post_id
            if id is None:
                continue

            # Complain about duplicate submissions
            if post_ids[id] > 1:
                transaction.link.errors.append(
                    "You've entered the same link (post #{0}) for multiple "
                    "transactions.".format(id)
                ) 
                no_dupes = False

            # If they're deliberately resubmitting this post, continue
            to_resubmit.append(id)
            if id in resubmitted_ids and transaction.notes.data:
                continue

            # If not, complain about past transactions
            for past_t in past_transaction_dict.get(id, []):
                message = ["You've claimed post #{0} before, and".format(id)]
                if past_t.state == 'pending':
                    message.append("it's still pending.")
                else:
                    message.append('it was {0}.'.format(past_t.state))

                message.append('If you really want to claim it again,')
                if not transaction.notes.data:
                    message.append('add a note explaining why and')
                message.append('press "Submit" again.')

                transaction.link.errors.append(' '.join(message))
                no_dupes = False

        self.resubmitted.data = ','.join(map(str, to_resubmit))
        return no_dupes

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

    correction = wtforms.IntegerField(validators=[
        wtforms.validators.Optional(),
        wtforms.validators.NumberRange(min=1, message='$1 minimum')
    ])

    notes = wtforms.TextField()

    def validate_correction(form, field):
        """Only allow a correction when approving a transaction."""

        if field.data is not None and form.what_do.data != 'approve':
            raise wtforms.validators.ValidationError(
                'You can only correct a transaction when approving it.'
            )

    def validate_notes(form, field):
        """Require a note when denying or correcting a transaction."""

        if not field.data.strip():
            if form.what_do.data == 'deny':
                raise wtforms.validators.ValidationError(
                    "Please include a note explaining why you're denying this "
                    "transaction."
                )
            elif form.correction.data is not None:
                raise wtforms.validators.ValidationError(
                    "Please include a note explaining why you're correcting "
                    "this transaction."
                )

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
        .filter_by(trainer_id=trainer.id)
    )

    last_ten = (
        base.filter(db.BankTransaction.state != 'pending')
        .order_by(db.BankTransaction.id.desc())
        .limit(10)
        .subquery().select()
    )

    current = base.filter_by(is_read=False)

    transactions = (
        current
        .union(last_ten)
        .order_by((db.BankTransaction.state == 'pending').desc(),
                  db.BankTransaction.is_read,
                  db.BankTransaction.id.desc())
        .all()
    )

    return itertools.groupby(transactions, recent_transaction_header)

def recent_transaction_header(transaction):
    """Return a string heading that this transaction should be sorted under
    under "recent transactions".  Also mark unread transactions as read.
    """

    if transaction.state == 'pending':
        return 'Pending'
    elif not transaction.is_read:
        transaction.is_read = True
        return 'Unread'
    else:
        return 'Recent'

@view_config(route_name='bank', request_method='GET', renderer='/bank.mako',
  permission='account.manage')
def bank(context, request):
    """The bank page."""

    stuff = {
        'allowance_form': None,
        'deposit_form': DepositForm(csrf_context=request.session),
        'recent_transactions': recent_transactions(request.user)
    }

    if can_collect_allowance(request.user):
        stuff['allowance_form'] = AllowanceForm(csrf_context=request.session)

    return stuff

@view_config(route_name='bank', request_method='POST', renderer='/bank.mako',
  permission='account.manage')
def bank_process(context, request):
    """Give the trainer their allowance, or let them deposit money."""

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
        # Validate
        valid = deposit_form.validate()
        valid = deposit_form.check_for_dupes(request) and valid
        if not valid:
            return stuff

        # Add the transactions
        for transaction_field in deposit_form.transactions:
            if transaction_field.amount.data:
                transaction = db.BankTransaction(
                    trainer_id=trainer.id,
                    amount=transaction_field.amount.data,
                    tcod_post_id=transaction_field.link.post_id
                )
                db.DBSession.add(transaction)

                # Add note, if applicable
                if transaction_field.notes.data:
                    db.DBSession.flush()
                    db.DBSession.add(db.BankTransactionNote(
                        bank_transaction_id=transaction.id,
                        trainer_id=trainer.id,
                        note=transaction_field.notes.data
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

        if field.notes.data:
            db.DBSession.add(db.BankTransactionNote(
                bank_transaction_id=transaction.id,
                trainer_id=approver.id,
                note=field.notes.data
            ))

        if field.what_do.data == 'ignore':
            continue
        elif field.what_do.data == 'approve':
            if field.correction.data is not None:
                transaction.amount = field.correction.data

            transaction.trainer.money += transaction.amount
            transaction.state = 'approved'
        elif field.what_do.data == 'deny':
            transaction.state = 'denied'

        transaction.approver_id = approver.id

    return httpexc.HTTPSeeOther('/bank/approve')

def transaction_month(transaction):
    """Return a header stating what month this transaction happened in, for
    the bank history page.
    """

    if transaction.date is None:
        return 'Older than 11 March 2015'
    else:
        return transaction.date.strftime('%B %Y')

@view_config(route_name='bank.history', request_method='GET',
  renderer='/bank_history.mako', permission='account.manage')
def bank_history(context, request):
    """A list of all the user's previous transactions."""

    transactions = (
        db.DBSession.query(db.BankTransaction)
        .filter_by(trainer_id=request.user.id)
        .order_by(db.BankTransaction.id.desc())
    )

    transactions = itertools.groupby(transactions, transaction_month)

    return {'transactions': transactions}
