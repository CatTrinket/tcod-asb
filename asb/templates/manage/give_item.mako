<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>Manage items - The Cave of Dragonflies ASB</%block>\

<%def name="give_header()">
<th>Give</th>
</%def>

<%def name="give(pokemon)">
<td class="button"><button name="pokemon" value="${pokemon.id | n, str}"
    type="submit">Give</button></td>
</%def>

<form action="${request.resource_url(item, 'give')}" method="POST">
% if csrf_failure:
<ul class="form-error">
    <li>Invalid CSRF token; the form probably expired.  Try again.</li>
</ul>
% endif
<input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
<h2>Active squad</h2>
${helpers.pokemon_table(request.user.squad,
    extra_left_cols=[(give_header, give)])}

<h2>PC</h2>
${helpers.pokemon_table(request.user.pc,
    extra_left_cols=[(give_header, give)])}
</form>
