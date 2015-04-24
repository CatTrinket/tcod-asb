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

<h1>${trainer.name}</h1>
% if trainer.ban is not None:
<p><strong>${trainer.name} was banned by ${trainer.ban.banned_by.name} for the
following reason: ${trainer.ban.reason}</strong></p>
<hr>
% endif

<dl>
    <dt>Forum profile</dt>
    <dd><a href="${profile_link}">Here</a></dd>

    <dt>Money</dt>
    <dd>$${trainer.money}</dd>

    <dt>Pokémon count</dt>
    <dd>${len(trainer.pokemon)}</dd>
</dl>

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

<h1>Battles</h1>

<table class="stats-table">
<thead>
    <tr>
        <th>Wins</th>
        <th>Losses</th>
        <th>Draws</th>
        <th>Total</th>
    </tr>
</thead>
<tbody>
<tr>
    <td>${len(wins)}</td>
    <td>${len(losses)}</td>
    <td>${len(draws)}</td>
    <td>${len(wins) + len(losses) + len(draws)}</td>
</tr>
</tbody>
</table>

% if wins or losses or draws or open_battles:
<p>
    <strong>Wins</strong>: ${len(wins)}
    <strong>Losses</strong>: ${len(losses)}
    <strong>Draws</strong>: ${len(draws)}
    <strong>Total</strong>: ${len(wins) + len(losses) + len(draws)}
</p>

${t.battle_table(wins, losses, draws, open_battles,
    subheaders=['Wins', 'Losses', 'Draws', 'In Progress'], show_end=True)}
% else:
<p>None yet!</p>
% endif
