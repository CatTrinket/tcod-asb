<%inherit file='/base.mako'/>\
<%block name='title'>${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<p>${pokemon.name} the ${pokemon.gender.name} ${pokemon.species.name} &lt;${pokemon.ability.name}&gt;\
% if pokemon.item is not None:
 @ ${pokemon.item.name}\
% endif
</p>

<p>Trainer: <a href="/trainers/${pokemon.trainer.identifier}">${pokemon.trainer.name}</a></p>
