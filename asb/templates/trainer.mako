<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

<h1>Pokémon</h1>
<h2>Active squad</h2>
<div class="stripy-rows">
${helpers.pokemon_table(trainer.squad, skip_cols=['trainer'])}
</div>

% if trainer.pc:
<h2>PC</h2>
${helpers.pokemon_table(trainer.pc, skip_cols=['trainer'])}
% endif

% if trainer.bag:
<h1>Bag</h1>
<ul>
    % for item in trainer.bag:
    <li>${item.name}</li>
    % endfor
</ul>
% endif
