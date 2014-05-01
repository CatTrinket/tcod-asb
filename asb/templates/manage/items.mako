<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>Manage items - The Cave of Dragonflies ASB</%block>\

<% tickies = iter(take_form.holders) %>
<%def name="take_item_ticky(pokemon)">
<td class="input ticky">${next(tickies) | n, str}</td>
</%def>

<%def name="ticky_header()">
<th></th>
</%def>

<p><a href="/items/buy">Buy items →</a></p>

<h1>Bag</h1>
<table>
<thead>
    <tr>
        <th colspan="2">Item</th>
        <th><abbr title="Quantity">Qty</abbr></th>
        <th>Give</th>
    </tr>
</thead>

<tbody>
    % for item, quantity in holdable:
    <tr>
        <td class="icon">
            <img src="/static/images/items/${item.identifier}.png" alt="">
        </td>
        <td>${helpers.link(item)}</td>
        <td class="stat">${quantity | n, str}</td>
        <td class="give"><a href="${request.resource_url(item, 'give')}">Give</a></td>
    </tr>
    % endfor
</tbody>
</table>
</form>

% if holders:
<h1>Held</h1>
% if take_form.errors:
<ul class="form-error">
   % for field, errors in take_form.errors.items():
   % for error in errors:
   <li>${error}</li>
   % endfor
   % endfor
</ul>
% endif

<form action="/items/manage" method="POST">
${take_form.csrf_token() | n, str}

${helpers.pokemon_table(holders, skip_cols=['item', 'trainer'],
    extra_left_cols=[
        (ticky_header, take_item_ticky),
        (helpers.item_header, helpers.item_cell),
    ]
)}

${take_form.take | n, str}
</form>
% endif
