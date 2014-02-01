<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${move.name} - Moves - The Cave of Dragonflies ASB</%block>\

<h1>${move.name}</h1>
<h2>Summary</h2>
<p>${move.summary}</p>

<h1>Effect</h1>
<p>${move.description}</p>

<h1>Pokémon</h1>
${helpers.pokemon_form_table(pokemon, squashed_forms=True)}
