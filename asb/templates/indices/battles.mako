<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Battles - The Cave of Dragonflies ASB</%block>\

% if request.has_permission('battle.open'):
<p><a href="/battles/new">Open a new battle →</a></p>
% endif

<h1>Current battles</h1>
% if open:
${t.battle_table(open)}
% else:
<p>None right now!</p>
% endif

<h1 id="waiting">Battles awaiting closure</h1>
% if approval:
${t.battle_table(approval, show_end=True)}
% else:
<p>None right now!</p>
% endif

<h1>Closed battles</h1>
% if closed:
${t.battle_table(closed, show_end=True)}
% else:
<p>None yet!</p>
% endif
