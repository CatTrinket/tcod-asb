<%inherit file='/base.mako'/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Manage Pokémon - Trainer Control Panel - The Cave of Dragonflies ASB</%block>\

<%
  if deposit is not None:
      d = iter(deposit.pokemon)
  if withdraw is not None:
      w = iter(withdraw.pokemon)
%>
<%def name="deposit_tickies(pokemon)">\
<td class="input ticky">${next(d)() | n}</td>
</%def>

<%def name="withdraw_tickies(pokemon)">\
<td class="input ticky">${next(w)() | n}</td>
</%def>

<%def name="ticky_col()">
<col class="ticky">
</%def>

<%def name="ticky_header()">
<th></th>
</%def>

<p><a href="/pokemon/buy">Buy Pokémon →</a></p>

% if deposit is not None:
<h1 id="squad">Active squad</h1>
% if deposit.errors:
<ul class="form-error">
    % for errors in deposit.errors.values():
    % for error in errors:
    <li>${error}</li>
    % endfor
    % endfor
</ul>
% endif

<form action="/pokemon/manage#squad" method="POST">
${deposit.csrf_token() | n}
${t.pokemon_table(trainer.squad, skip_cols=['trainer'],
    extra_left_cols=[{'col': ticky_col, 'th': ticky_header, 'td': deposit_tickies}])}
${deposit.submit() | n}
</form>
% endif

% if withdraw is not None:
<h1 id="pc">PC</h1>
% if withdraw.errors:
<ul class="form-error">
    % for errors in withdraw.errors.values():
    % for error in errors:
    <li>${error}</li>
    % endfor
    % endfor
</ul>
% endif

<form action="/pokemon/manage#pc" method="POST">
${withdraw.csrf_token() | n}
${t.pokemon_table(trainer.pc, skip_cols=['trainer'],
    extra_left_cols=[{'col': ticky_col, 'th': ticky_header, 'td': withdraw_tickies}])}
${withdraw.submit() | n}
</form>
% endif
