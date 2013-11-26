<%inherit file='/base.mako'/>\
<%block name='title'>Items - The Cave of Dragonflies ASB</%block>\

<table id="item-table">
<thead>
<tr>
    <th>Item</th>
    <th>Summary</th>
</tr>
</thead>

<tbody>
% for item in items:
<tr>
    <td><a href="/items/${item.identifier}">${item.name}</a></td>
    <td>${item.summary}</td>
</tr>
% endfor
</tbody>
</table>
