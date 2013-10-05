<%inherit file='/base.mako'/>\
<%block name='title'>${trainer.name} - Trainers</%block>\
<%namespace name="helpers" file="/helpers.mako"/>\

<h1>${trainer.name}</h1>

% for label, pokemon_list in [('Squad', trainer.squad), ('PC', trainer.pc)]:
<h3>${label}</h3>
<table>
<tr>
    <th>Name</th>
    <th>Species</th>
    <th>⚥</th>
    <th>Ability</th>
    <th>Item</th>
</tr>

% for pokemon in pokemon_list:
<tr>
    <td><a href="/pokemon/${pokemon.identifier}">${pokemon.name}</a></td>
    <td><a href="/pokemon/species/${pokemon.species.identifier}">${pokemon.species.name}</a></td>
    <td>${helpers.gender_symbol(pokemon.gender)}</td>
    <td>${pokemon.ability.name}</td>
    <td>\
% if pokemon.item:
${pokemon.item.name}\
% endif
</td>
</tr>
% endfor
</table>
% endfor

<h3>Bag</h3>
<ul>
    % for item in trainer.bag:
    <li>${item.name}</li>
    % endfor
</ul>
</p>
