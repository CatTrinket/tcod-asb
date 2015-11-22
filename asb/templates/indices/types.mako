<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Types - The Cave of Dragonflies ASB</%block>\

<h1>Type chart</h1>
<table id="type-chart">
<colgroup>
    <col id="left-axis">
    <col class="type-col">
</colgroup>

<colgroup id="matchups">
    % for n in range(len(types)):
    <col>
    % endfor
</colgroup>

<thead>
    <tr>
        <th colspan="2" rowspan="2"></th>
        <th colspan=${len(types)}>Defending type</th>
    </tr>

    <tr id="defending-types">
        % for type in types:
        <th>${h.type_icon(type)}</th>
        % endfor
    </tr>
</thead>

<tbody>
    % for (n, type) in enumerate(types):
    <tr>
        % if n == 0:
        <th rowspan=${len(types)} id="left-axis-label"><span>Attacking type</span></th>
        % endif

        <th>${h.type_icon(type)}</th>
        % for matchup in type.attacking_matchups:
        % if matchup.result.identifier == 'neutral':
        <td></td>
        % elif matchup.result.identifier == 'super-effective':
        <td class="super-effective">+</td>
        % elif matchup.result.identifier == 'not-very-effective':
        <td class="not-very-effective">−</td>
        % else:
        <td class="ineffective">X</td>
        % endif
        % endfor
    </tr>
    % endfor
</tbody>
</table>
