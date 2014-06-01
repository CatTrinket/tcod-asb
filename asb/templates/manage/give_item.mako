<%inherit file='/base.mako'/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Manage items - The Cave of Dragonflies ASB</%block>\

<%def name="give_col()">
<col class="give">
</%def>

<%def name="give_header()">
<th>Give</th>
</%def>

<%def name="give(pokemon)">
<td class="input"><button name="pokemon" value="${pokemon.id}"
    type="submit">Give</button></td>
</%def>

<form action="${request.resource_url(item, 'give')}" method="POST">
% if csrf_failure:
<ul class="form-error">
    <li>Invalid CSRF token; the form probably expired.  Try again.</li>
</ul>
% endif
<input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
${t.pokemon_table(
    request.user.squad, request.user.pc,
    subheaders=['Active squad', 'PC'],
    skip_cols=['trainer'],
    extra_left_cols=[{'col': give_col, 'th': give_header, 'td': give}]
)}
</form>
