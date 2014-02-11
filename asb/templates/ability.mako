<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${ability.name} - Abilities - The Cave of Dragonflies ASB</%block>\

<h1>${ability.name}</h1>
<p>${ability.description}</p>

<h1>Pokémon</h1>
% if normal_pokemon:
<h2>Regular ability</h2>
${helpers.pokemon_form_table(normal_pokemon, squashed_forms=True)}
% endif

% if hidden_pokemon:
<h2>Hidden ability</h2>
${helpers.pokemon_form_table(hidden_pokemon, squashed_forms=True)}
% endif
