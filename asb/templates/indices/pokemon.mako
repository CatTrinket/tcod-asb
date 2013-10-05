<%inherit file='/base.mako'/>\
<%block name='title'>Pokémon</%block>\
<%namespace name="helpers" file="/helpers.mako"/>\

<table>
<tr>
    <th>Name</th>
    <th>Species</th>
    <th>⚥</th>
    <th>Trainer</th>
    <th>Ability</th>
    <th>Item</th>
</tr>

% for p in pokemon:
<tr>
    <td><a href="/pokemon/${p.identifier}">${p.name}</a></td>
    <td><a href="/pokemon/species/${p.species.identifier}">${p.species.name}</a></td>
    <td>${helpers.gender_symbol(p.gender)}</td>
    <td><a href="/trainers/${p.trainer.identifier}">${p.trainer.name}</a></td>
    <td>${p.ability.name}</td>
    <td>\
% if p.item:
${p.item.name}\
% endif
</td>
</tr>
% endfor
</table>
