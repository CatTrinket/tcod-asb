<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<p>AW YEAH, POKÉMON #${pokemon.species.number} IS <strong>${pokemon.name.upper()}</strong></p>

<p>IT'S A FREAKING ${"/".join(type.name.upper() for type in pokemon.types)} TYPE.</p>

<%
    abilities = set(ability.ability.name.upper() for ability in pokemon.abilities)
%>

<p>TAKE A GOOD LOOK AT <strong>${"THAT ABILITY" if len(abilities) == 1 else "THOSE ABILITIES"}</strong>: ${" AND ".join(abilities)}</p>

<h1>Moves</h1>
${helpers.move_table(pokemon.moves)}
