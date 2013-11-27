<%inherit file='/base.mako'/>\
<%block name='title'>Moves - The Cave of Dragonflies ASB</%block>\

<table class="effect-table">
<thead>
<tr>
    <th>Move</th>
    <th>Type</th>
    <th><abbr title="Base damage">Dmg</abbr></th>
    <th><abbr title="Base energy cost">En.</abbr></th>
    <th><abbr title="Accuracy">Acc.</abbr></th>
    <th>Summary</th>
</tr>
</thead>

<tbody>
% for move in moves:
<tr>
    <td class="focus-column"><a href="/moves/${move.identifier}">${move.name}</a></td>

    <td><span class="type type-${move.type.identifier}">${move.type.name}</span></td>

    % if move.damage is None:
    <td class="stat">—</td>
    % elif move.damage == -1:
    <td class="stat">*</td>
    % else:
    <td class="stat">${move.damage | n, str}%</td>
    % endif

    % if move.energy is None:
    <td class="stat">—</td>
    % elif move.energy == -1:
    <td class="stat">*</td>
    % elif move.energy == 0:
    <td class="stat">?</td>
    % else:
    <td class="stat">${move.energy | n, str}%</td>
    % endif

    % if move.accuracy is None:
    <td class="stat">—</td>
    % else:
    <td class="stat">${move.accuracy | n, str}%</td>
    % endif

    <td>${move.summary}</td>
</tr>
% endfor
</tbody>
</table>
