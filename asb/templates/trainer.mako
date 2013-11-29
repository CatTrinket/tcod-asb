<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

<h1>Active squad</h1>
<div class="stripy-rows">
${helpers.pokemon_table(trainer.squad, skip_cols=['trainer'])}
</div>

% if trainer.pc:
<h1>PC</h1>
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
