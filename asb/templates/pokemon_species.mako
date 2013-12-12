<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<p>AW YEAH, POKÉMON #${pokemon.species.number} IS <strong>${pokemon.name.upper()}</strong></p>

<h1>Moves</h1>
${helpers.move_table(pokemon.moves)}
