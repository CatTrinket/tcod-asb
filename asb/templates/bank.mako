<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>Bank - The Cave of Dragonflies ASB</%block>\
<% from asb.tcodf import post_link %>

<%def name="transaction_tbody(transactions, header, reason_column=True)">
% if transactions:
<tbody>
    <tr class="subheader-row"><td colspan="3">${header}</td></tr>

    % for transaction in transactions:
    <tr>
        <td class="price">$${transaction.amount}</td>

        <td><a href="${post_link(transaction.tcod_post_id)}">
            Post #${transaction.tcod_post_id}
        </a></td>

        % if reason_column:
        <td>${transaction.reason or ''}</td>
        % endif
    </tr>
    % endfor
</tbody>
% endif
</%def>

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

<table>
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

% if any(recent_transactions.values()):
<% denied = bool(recent_transactions['denied']) %>
<h1 id="recent">Recent transactions</h1>
<table>
<thead>
    <tr>
        <th>Amount</th>
        <th>Link</th>
        % if denied:
        <th>Reason</th>
        % endif
    </tr>
</thead>
${transaction_tbody(recent_transactions['pending'], 'Pending', denied)}
${transaction_tbody(recent_transactions['approved'], 'Approved', denied)}
${transaction_tbody(recent_transactions['denied'], 'Denied')}
</table>

% if clear_form is not None:
<form action="/bank" method="POST">
${clear_form.csrf_token}
${clear_form.clear}
${h.form_error_list(*clear_form.errors.values())}
</form>
% endif
% endif
