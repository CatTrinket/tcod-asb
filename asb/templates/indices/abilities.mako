<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Abilities - The Cave of Dragonflies ASB</%block>\

<%! from asb.markup.markdown import render as md %>

<table class="standard-table effect-table">
<col class="ability">
<col class="summary">
<thead>
<tr>
    <th>Ability</th>
    <th>Summary</th>
</tr>
</thead>

<tbody>
% for ability in abilities:
<tr>
    <td class="focus-column">${h.link(ability)}</td>
    <td>${ability.summary | md}</td>
</tr>
% endfor
</tbody>
</table>
