<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>Approve transactions - Bank - The Cave of Dragonflies ASB</%block>\

<dl id="bank-approval-instructions">
    <dt>I</dt>
    <dd>Ignore for now</dd>

    <dt>A</dt>
    <dd>Approve</dd>

    <dt>D</dt>
    <dd>Deny</dd>
</dl>

<form action="/bank/approve" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<table>
<thead>
<tr>
    <th><abbr title="Ignore for now">I</abbr></th>
    <th><abbr title="Approve">A</abbr></th>
    <th><abbr title="Deny">D</abbr></th>
    <th>Trainer</th>
    <th>Amount</th>
    <th>Link</th>
    <th>Reason (if applicable)</th>
</tr>
</thead>

<tbody>
% for transaction in form.transactions:
<tr>
    % for option in transaction.what_do:
    <td class="input">${option() | n}</td>
    % endfor

    <td>${h.link(transaction.transaction.trainer)}</td>
    <td class="price">$${transaction.transaction.amount | n, str}</td>
    <td>
        <a href="${transaction.transaction.link}">
            Post #${transaction.transaction.tcod_post_id | n, str}
        </a>
    </td>
    <td class="input">${transaction.reason(size=60) | n}</td>
</tr>

% for field, errors in transaction.errors.items():
<tr>
    <td colspan="7" class="form-error">
        ${field.capitalize()}: ${', '.join(errors)}
    </td>
</tr>
% endfor
% endfor
</tbody>
</table>

${form.submit() | n}
</form>
