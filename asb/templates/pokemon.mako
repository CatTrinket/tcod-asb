<%inherit file='/base.mako'/>\
<%block name='title'>${pokemon.name} - Pokémon</%block>\

<p>AW YEAH, POKÉMON #${str(pokemon.id)} IS <strong>${pokemon.name.upper()}</strong> THE ${pokemon.gender.name.upper()} ${pokemon.species.name.upper()}</p>
