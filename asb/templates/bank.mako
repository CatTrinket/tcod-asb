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
    ${allowance_form.collect() | n}
</form>
% else:
<p>You have already collected this week's allowance.</p>
% endif

<h1>Deposit</h1>
<p>(this part doesn't actually work yet)</p>

<form>
<table>
<thead>
    <tr>
        <th>Amount</th>
        <th>Link</th>
    </tr>
</thead>

<tbody>
    % for n in range(5):
    <tr>
        <td class="input">$<input type="text" maxlength="3" size="3"></td>
        <td class="input"><input type="text" size="60"></td>
    </tr>
    % endfor

    <tr>
        <td class="input" colspan="2"><button>+</button></td>
    </tr>
</tbody>
</table>

<button>Submit</button>
</form>
