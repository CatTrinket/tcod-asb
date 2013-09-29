<%inherit file='/base.mako'/>\
<%block name='title'>${trainer.name} - Trainers</%block>\

<h1>${trainer.name}</h1>


% for label, pokemon_list in [('Squad', trainer.squad), ('PC', trainer.pc)]:
<p>
    ${label}:
    <ul>
        % for pokemon in pokemon_list:
        <li><strong>${pokemon.name}</strong> the ${pokemon.gender.name} ${pokemon.species.name} &lt;${pokemon.ability.name}&gt;\
% if pokemon.item:
 @ ${pokemon.item.name}\
% endif
</li>
        % endfor
    </ul>
</p>
% endfor

<p>
    Bag:
    <ul>
        % for item in trainer.bag:
        <li>${item.name}</li>
        % endfor
    </ul>
</p>
