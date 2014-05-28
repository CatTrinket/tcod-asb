<%inherit file='/base.mako'/>\
<%block name='title'>Bank - The Cave of Dragonflies ASB</%block>\

<p><b>Your balance:</b> $${request.user.money | n, str}</p>

<h1>Allowance</h1>
<p>Every Friday, each member of the ASB league is offered $3 in allowance.
You have all week to claim your allowance, but if you miss a week, you miss a
week.</p>

% if allowance_form is not None:
<form id="allowance" action="/bank" method="POST">
    ${allowance_form.csrf_token() | n}
    ${allowance_form.collect_allowance() | n}
</form>
% else:
<p>You have already collected this week's allowance.</p>
% endif

<h1>Deposit/Withdraw</h1>
<form id="deposit" action="/bank" method="POST">
${deposit_form.csrf_token() | n}

% if deposit_form.csrf_token.errors:
<ul class="form-error">
    % for error in deposit_form.csrf_token.errors:
    <li>${error}</li>
    % endfor
</ul>
% endif

<!-- This button actually appears at the end of the form; this is just a hidden
duplicate to control which button gets "clicked" when the user hits enter -->
${deposit_form.deposit(style="display: none;") | n}

<table id="deposit-withdraw">
<thead>
    <tr>
        <th>Amount</th>
        <th>Link</th>
    </tr>
</thead>

<tbody>
    % for transaction_form in deposit_form.transactions:
    <tr>
        <td class="input">
            $${transaction_form.amount(maxlength=3, size=3) | n}
        </td>

        <td class="input">
            ${transaction_form.link(size=60) | n}
        </td>
    </tr>

    % for field, errors in transaction_form.errors.items():
    <tr>
        <td class="form-error" colspan="2">
            ${field.capitalize()}: ${', '.join(errors)}
        </td>
    </tr>
    % endfor

    % endfor

    <tr>
        <td class="input" colspan="2">${deposit_form.add_rows() | n}</td>
    </tr>
</tbody>
</table>

${deposit_form.deposit() | n}
</form>
