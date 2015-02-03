<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md, chomp %>

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
<table class="standard-table effect-table">
<col class="icon item-icon">
<col class="item">
<col class="stat">
<col class="summary">
<thead>
    <tr>
        <th colspan="2">Item</th>
        <th><abbr title="Quantity">Qty</th>
        <th>Summary</th>
    </tr>
</thead>
<tbody>
    % for (item, qty) in trainer.bag:
    <tr>
        <td class="icon item-icon">
            <img src="/static/images/items/${item.identifier}.png" alt="">
        </td>
        <td class="focus-column">${h.link(item)}</td>
        <td class="stat">${qty}</td>
        <td>${item.summary | md.convert, chomp, n}</td>
    </tr>
    % endfor
</tbody>
</table>
% endif
