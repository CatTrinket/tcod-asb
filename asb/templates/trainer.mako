<%inherit file='/base.mako'/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

% if request.has_permission('trainer.edit'):
<p><a href="${request.resource_url(trainer, 'edit')}">
    Edit ${trainer.name} →
</a></p>
% endif

<h1>Pokémon</h1>
${t.pokemon_table(
    trainer.squad, trainer.pc,
    subheaders=['Active squad', 'PC'],
    subheader_colspan=9,
    skip_cols=['trainer']
)}

% if trainer.bag:
<h1>Bag</h1>
<ul>
    % for item in trainer.bag:
    <li>${item.name}</li>
    % endfor
</ul>
% endif
