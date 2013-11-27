<%inherit file='/base.mako'/>\
<%block name='title'>Abilities - The Cave of Dragonflies ASB</%block>\

<table class="effect-table">
<thead>
<tr>
    <th>Ability</th>
    <th>Summary</th>
</tr>
</thead>

<tbody>
% for ability in abilities:
<tr>
    <td class="focus-column"><a href="/abilities/${ability.identifier}">${ability.name}</a></td>
    <td>${ability.summary}</td>
</tr>
% endfor
</tbody>
</table>
