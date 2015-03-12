<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%namespace name='t' file='/helpers/tables.mako'/>\
<%block name='title'>Bank - The Cave of Dragonflies ASB</%block>\
<% from asb.tcodf import post_link %>

<p><b>Your balance:</b> $${request.user.money}</p>

<h1>Fifth United Bank of the Cave of Dragonflies</h1>

<p>Welcome to your ASB bank account!  Long past the days of having to make
multiple posts every single time you plan on making money or throwing it on
other people, you simply have a terminal before you that will handle your
transactions and hook them up with an approver — quick, easy, and
automatic.</p>

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

<h1>Deposit</h1>
<form id="deposit" action="/bank" method="POST">
${deposit_form.resubmitted()}
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

<table class="transactions">
<thead>
    <tr>
        <th>Amount</th>
        <th>Link</th>
        <th>Notes (optional)</th>
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

        <td class="input">
            ${transaction_form.notes(size=60, maxlength=200) | n}
        </td>
    </tr>

    % if transaction_form.errors:
    <tr>
        <td colspan="3">
            ${h.form_error_list(*transaction_form.errors.values())}
        </td>
    </tr>
    % endif
    % endfor

    <tr>
        <td class="input" colspan="3">${deposit_form.add_rows() | n}</td>
    </tr>
</tbody>
</table>

${deposit_form.deposit() | n}
</form>

<h1 id="recent">Recent transactions</h1>
<p><a href="/bank/history">Full history →</a></p>
${t.transaction_table(recent_transactions)}
