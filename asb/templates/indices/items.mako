<%inherit file='/base.mako'/>\
<%block name='title'>Items - The Cave of Dragonflies ASB</%block>\
<% from asb.markdown import md, chomp %>

% if request.has_permission('account.manage'):
<p><a href="/items/buy">Buy items →</a></p>
% endif

<table class="standard-table effect-table">
<col class="item-icon">
<col class="item">
<col class="price">
<thead>
<tr>
    <th colspan="2">Item</th>
    <th>Price</th>
    <th>Summary</th>
</tr>
</thead>

% for category in item_categories:
<tbody>
    <tr class="subheader-row">
        <td colspan="4">${category.name}</td>
    </tr>

    % for item in category.items:
    <tr>
        <td class="icon"><img src="/static/images/items/${item.identifier}.png" alt=""></td>
        <td class="focus-column"><a href="/items/${item.identifier}">${item.name}</a></td>
        % if item.price is not None:
        <td class="price">$${item.price | n, str}</td>
        % else:
        <td class="price">—</td>
        % endif
        <td>${item.summary | md.convert, chomp, n}</td>
    </tr>
    % endfor
</tbody>
% endfor
</table>
