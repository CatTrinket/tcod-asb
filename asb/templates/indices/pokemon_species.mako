<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>Pokémon species - The Cave of Dragonflies ASB</%block>\

<%def name="pop_header()">\
<th><abbr title="Population">Pop.</abbr></th>\
</%def>

<%def name="pop_cell(pkmn)">\
% if pokemon[pkmn] is None:
<td class="stat population-zero">0</td>\
% else:
<td class="stat">${helpers.link(pkmn, text=str(pokemon[pkmn]), anchor='census')}</td>\
% endif
</%def>

${helpers.pokemon_form_table(pokemon, extra_right_cols=[(pop_header, pop_cell)])}
