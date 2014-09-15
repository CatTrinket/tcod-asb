<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Battles - The Cave of Dragonflies ASB</%block>\

<%def name="battle_table(battles, show_end=False)">
<table>
<thead>
    <tr>
        <th>Battle</th>
        <th>Ref</th>
        <th>Started</th>
        % if show_end:
        <th>Ended</th>
        % endif
    </tr>
</thead>

<tbody>
    % for battle in battles:
    <tr>
        <td class="focus-column">${h.link(battle)}</td>

        % if battle.ref is None:
        <td>???</td>
        % else:
        <td>${h.link(battle.ref)}</td>
        % endif

        <td>${battle.start_date.strftime('%Y %B %d')}</td>

        % if show_end:
        <td>${battle.end_date.strftime('%Y %B %d')}</td>
        % endif
    </tr>
    % endfor
</tbody>
</table>
</%def>

% if request.has_permission('battle.open'):
<p><a href="/battles/new">Open a new battle →</a></p>
% endif

<h1>Current battles</h1>
% if open:
${battle_table(open)}
% else:
<p>None right now!</p>
% endif

<h1 id="waiting">Battles awaiting closure</h1>
% if approval:
${battle_table(approval, show_end=True)}
% else:
<p>None right now!</p>
% endif

<h1>Closed battles</h1>
% if closed:
${battle_table(closed, show_end=True)}
% else:
<p>None yet!</p>
% endif
