<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Pokémon species - The Cave of Dragonflies ASB</%block>\

<%def name="pop_col()">
<col class="population">
</%def>

<%def name="pop_header()">\
<th><abbr title="Population">Pop.</abbr></th>\
</%def>

<%def name="pop_cell(a_pokemon)">\
% if pokemon[a_pokemon] is None:
<td class="stat population-zero">0</td>\
% else:
<td class="stat">${h.link(a_pokemon, text=str(pokemon[a_pokemon]),
    anchor='census')}</td>\
% endif
</%def>

${t.pokemon_form_table(
    pokemon,
    extra_right_cols=[{'col': pop_col, 'th': pop_header, 'td': pop_cell}]
)}
