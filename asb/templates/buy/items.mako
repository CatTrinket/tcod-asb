<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Buy items - The Cave of Dragonflies ASB</%block>\

<form action="/items/buy" method="POST">
${quick_buy.csrf_token() | n}
${quick_buy.item.label() | n}:
${quick_buy.item(placeholder='Enter an item') | n}
${quick_buy.quick_buy() | n}

% if quick_buy.errors:
<ul class="form-error">
    % for errors in quick_buy.errors.values():
    % for error in errors:
    <li>${error}</li>
    % endfor
    % endfor
</ul>
% endif
</form>

% if cart is not None:
<%
    total = 0
    errors = []
    errors.extend(cart_form.csrf_token.errors)
    errors.extend(cart_form.buy.errors)
%>
<h1>Cart</h1>
<form action="/items/buy" method="POST">
${cart_form.csrf_token() | n}

<table class="standard-table">
<col class="item-icon">
<col class="item">
<col class="price">
<col class="input-small">
<col class="price">

<thead>
<tr>
    <th colspan="2">Item</th>
    <th>Price</th>
    <th><abbr title="Quantity">Qty</abbr></th>
    <th>Total</th>
</tr>
</thead>
<tbody>
    % for item, field in zip(cart, cart_form.items):
    <%
        quantity = field.default
        price = item.price * quantity
        total += price
        errors.extend('{}: {}'.format(item.name, error) for error in field.errors)
    %>
    <tr>
        <td class="icon"><img src="/static/images/items/${item.identifier}.png" alt=""></td>
        <td class="focus-column">${h.link(item)}</td>
        <td class="price">$${item.price}</td>
        <td class="input">${field(size=2) | n}</td>
        <td class="price">$${price}</td>
    </tr>
    % endfor
</tbody>

<tfoot>
    <tr>
        <td class="focus-column" colspan="4">Total</td>
        <td class="price">$${total}</td>
    </tr>
    <% remaining_money = request.user.money - total %>
    <tr class="${'unaffordable-total' if remaining_money < 0 else ''}">
        <td class="focus-column" colspan="4">Bank minus total</td>
        <td class="price">$${h.num(remaining_money)}</td>
    </tr>
</tfoot>
</table>

${h.form_error_list(cart_form.csrf_token.errors, errors)}

${cart_form.update() | n}
% if remaining_money >= 0:
${cart_form.buy() | n}
% endif
</form>
% else:
<p>Your bank balance: $${request.user.money}</p>
% endif

<h1>Browse</h1>
<form action="/items/buy" method="POST">
${browse.csrf_token()}
${h.form_error_list(*browse.errors.values())}

<table class="standard-table effect-table">
<col class="input-small">
<col class="item-icon">
<col class="item">
<col class="price">
<col class="summary">

<thead>
    <tr>
        <th></th>
        <th colspan="2">Item</th>
        <th>Price</th>
        <th>Summary</th>
    </tr>
</thead>

% for category, items in browse.categorized_items():
<tbody>
    <tr class="subheader-row">
        <td colspan="5">${category.name}</td>
    </tr>

    % for item, button in items:
    <tr>
        <td class="input">${button}</td>
        <td class="icon"><img src="/static/images/items/${item.identifier}.png" alt=""></td>
        <td class="focus-column"><a href="/items/${item.identifier}">${item.name}</a></td>
        <td class="price">$${item.price}</td>
        <td>${item.summary}</td>
    </tr>
    % endfor
</tbody>
% endfor
</table>
</form>
