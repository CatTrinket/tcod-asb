<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>Transactions awaiting approval - Bank - The Cave of Dragonflies ASB</%block>\

<h1>Transactions awaiting approval</h1>

<ul>
    <li>If someone has claimed a legitimate transaction, but for the wrong
    amount, type in the correct amount beside the amount they claimed, and
    approve it.</li>

    <li>Leaving a note is required when denying or editing a transaction, and
    optional otherwise.</li>

    <li>Your own transactions will not appear here.</li>
</ul>

<ul>
    <li><b>I:</b> Ignore for now</li>
    <li><b>A:</b> Approve</li>
    <li><b>D:</b> Deny</li>
</ul>

<form action="/bank/approve" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<table class="transactions">
<thead>
<tr>
    <th><abbr title="Ignore for now">I</abbr></th>
    <th><abbr title="Approve">A</abbr></th>
    <th><abbr title="Deny">D</abbr></th>
    <th>Trainer</th>
    <th><abbr title="Amount">Amt</abbr></th>
    <th><abbr title="Correction">Corr.</abbr></th>
    <th>Link</th>
    <th>Notes</th>
</tr>
</thead>

<tbody>
% for transaction in form.transactions:
<tr>
    % for option in transaction.what_do:
    <td class="input">${option() | n}</td>
    % endfor

    <td>${h.link(transaction.transaction.trainer)}</td>
    <td class="price">$${transaction.transaction.amount}</td>
    <td class="input">$${transaction.correction(size=2, maxlength=3)}</td>
    <td>
        <a href="${transaction.transaction.link}">
            Post #${transaction.transaction.tcod_post_id}
        </a>
    </td>

    <td class="notes">
        <ul>
            % for note in transaction.transaction.notes:
            % if note.trainer is None:
            <li>??? said: ${note.note}</li>
            % elif note.trainer == request.user:
            <li>You said: ${note.note}</li>
            % else:
            <li>${note.trainer.name} said: ${note.note}</li>
            % endif
            % endfor

            % for prev_trans in transaction.transaction.previous_transactions:
            <li>
                % if prev_trans.state == 'pending':
                ${prev_trans.trainer.name} has another claim for this post
                above.
                % else:
                ${prev_trans.trainer.name} claimed this post in a previous
                transaction.  It was ${prev_trans.state}

                % if prev_trans.approver is None:
                by someone
                % elif prev_trans.approver == request.user:
                by you
                % else:
                by ${prev_trans.approver.name}
                % endif

                % if not prev_trans.notes:
                and had no notes.
                % else:
                and had the following notes:

                <ul>
                    % for prev_note in prev_trans.notes:
                    % if prev_note.trainer is None:
                    <li>??? said: ${prev_note.note}</li>
                    % elif prev_note.trainer == request.user:
                    <li>You said: ${prev_note.note}</li>
                    % else:
                    <li>${prev_note.trainer.name} said: ${prev_note.note}</li>
                    % endif
                    % endfor
                </ul>
                % endif
                % endif
            </li>
            % endfor

            <li>${transaction.notes(size=60, placeholder='Add a note') | n}</li>

            % for (field, errors) in transaction.errors.items():
            % for error in errors:
            <li class="form-error">${error}</li>
            % endfor
            % endfor
        </ul>

    </td>
</tr>
% endfor
</tbody>
</table>

${form.submit() | n}
</form>
