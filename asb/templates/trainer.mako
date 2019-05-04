<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="markup" file="/helpers/markup.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

<%! from asb.markup.markdown import render as md %>

% if request.has_permission('trainer.edit'):
    <p><a href="${request.resource_url(trainer, 'edit')}">
        Edit ${trainer.name} →
    </a></p>
% endif

% if request.has_permission('trainer.edit.profile'):
    <p><a href="${request.resource_url(trainer, 'profile')}">
        % if trainer == request.user:
            Edit your profile →
        % else:
            Edit ${trainer.name}'s profile →
        % endif
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
    <dd>${len(trainer.squad) + len(trainer.pc)}</dd>
</dl>

% if trainer.profile is not None:
    <h2>Profile</h2>
    ${markup.markup(trainer.profile, trainer.profile_format)}
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
        <td>${item.summary | md}</td>
    </tr>
    % endfor
</tbody>
</table>
% endif

% if wins or losses or draws or open_battles:
<h1>Battles</h1>
<%
    num_wins = len(wins)
    num_losses = len(losses)
    num_draws = len(draws)
    total_completed = num_wins + num_losses + num_draws
%>

% if total_completed:
<dl class="battle-stats">
    <dt>Wins</dt>
    <dd>${num_wins}</dd>

    <dt>Losses</dt>
    <dd>${num_losses}</dd>

    <dt>Draws</dt>
    <dd>${num_draws}</dd>

    <dt>Total</dt>
    <dd>${total_completed}</dd>
</dl>
% endif

${t.battle_table(open_battles, wins, losses, draws,
    subheaders=['In Progress', 'Wins', 'Losses', 'Draws'], show_end=True)}
% endif

% if ref_open or ref_done:
<h1>Battles Reffed</h1>

${t.battle_table(
    ref_open, ref_done,
    subheaders=['In Progress', 'Past'],
    show_end=True)}
% endif
