<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Manage items - The Cave of Dragonflies ASB</%block>\

<%def name="give_col()">
<col class="give">
</%def>

<%def name="give_header()">
<th>Give</th>
</%def>

<% buttons = iter(form.pokemon) %>
<%def name="give(pokemon)">
<td class="input">${next(buttons)}</td>
</%def>

<h1>Give ${item.name}</h1>

<form action="${request.resource_url(item, 'give')}" method="POST">
${form.csrf_token}
${h.form_error_list(*form.errors.values())}

${t.pokemon_table(
    *pokemon,
    subheaders=['Active Squad' if group[0].is_in_squad else 'PC'
                for group in pokemon],
    skip_cols=['trainer'],
    extra_left_cols=[{'col': give_col, 'th': give_header, 'td': give}]
)}
</form>
