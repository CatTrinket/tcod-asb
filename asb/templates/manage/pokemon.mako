<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>Manage Pokémon - Trainer Control Panel - The Cave of Dragonflies ASB</%block>\

<%
  if deposit is not None:
      d = iter(deposit.pokemon)
  if withdraw is not None:
      w = iter(withdraw.pokemon)
%>
<%def name="deposit_tickies(pokemon)">\
<td class="input ticky">${next(d) | n, str}</td>
</%def>

<%def name="withdraw_tickies(pokemon)">\
<td class="input ticky">${next(w) | n, str}</td>
</%def>

<%def name="ticky_header()">
<th></th>
</%def>

<a href="/pokemon/buy">Buy Pokémon →</a>

% if deposit is not None:
<h1 id="squad">Active squad</h1>
% if deposit.errors:
<ul class="form-error">
    % for errors in deposit.errors.values():
    % for error in errors:
    <li>${error | n, str}</li>
    % endfor
    % endfor
</ul>
% endif

<form action="/pokemon/manage#squad" method="POST">
${deposit.csrf_token | n, str}
${helpers.pokemon_table(trainer.squad, skip_cols=['trainer'],
    extra_left_cols=[(ticky_header, deposit_tickies)])}
${deposit.submit | n, str}
</form>
% endif

% if withdraw is not None:
<h1 id="pc">PC</h1>
% if withdraw.errors:
<ul class="form-error">
    % for errors in withdraw.errors.values():
    % for error in errors:
    <li>${error | n, str}</li>
    % endfor
    % endfor
</ul>
% endif

<form action="/pokemon/manage#pc" method="POST">
${withdraw.csrf_token | n, str}
${helpers.pokemon_table(trainer.pc, skip_cols=['trainer'],
    extra_left_cols=[(ticky_header, withdraw_tickies)])}
${withdraw.submit | n, str}
</form>
% endif
