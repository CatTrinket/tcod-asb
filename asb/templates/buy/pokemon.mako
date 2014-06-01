<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Buy Pokémon - The Cave of Dragonflies ASB</%block>\
<%
    rarity_labels = [
        'Rarity One',
        'Rarity Two',
        'Rarity Three',
        'Rarity Four',
        'Rarity Five',
        'Rarity Six',
        'Rarity Seven',
        'Rarity Eight'
    ]
%>

<%def name="add_to_cart_col()">
<col class="input-small">
</%def>

<%def name="add_to_cart_cell(pokemon)">
<td class="input"><button name="add" value="${pokemon.species.identifier}">+</button></td>
</%def>

<form action="/pokemon/buy" method="POST">
${quick_buy.csrf_token() | n}
Quick buy: ${quick_buy.pokemon(placeholder='Enter a Pokémon') | n}
${quick_buy.quickbuy() | n}
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

% if cart:
<% total = 0 %>
<h1>Cart</h1>
<form action="/pokemon/buy" method="POST">
<table class="standard-table">
<col class="input-small">
<col class="pokemon-icon">
<col class="pokemon-species">
<col class="price">
<thead>
  <tr>
    <th></th>
    <th colspan="2">Pokémon</th>
    <th>Price</th>
  </tr>
</thead>
<tbody>
  % for pokemon in cart:
  <tr>
    <td class="input"><button name="remove" value="${pokemon.identifier}">X</button></td>
    <td class="icon">${h.pokemon_form_icon(pokemon.default_form)}</td>
    <td class="focus-column">${h.link(pokemon.default_form, text=pokemon.name)}</td>
    <td class="price">$${pokemon.rarity.price}</td>
  </tr>
  <% total += pokemon.rarity.price %>
  % endfor
</tbody>
<tfoot>
  <tr>
    <td colspan="3" class="focus-column">Total</td>
    <td class="price">$${total}</td>
  </tr>
  <% remaining_money = request.user.money - total %>
  <tr class="${'unaffordable-total' if remaining_money < 0 else ''}">
    <td colspan="3" class="focus-column">Bank minus total</td>
    <td class="price">$${h.num(remaining_money)}</td>
  </tr>
</tfoot>
</table>
</form>
% if remaining_money >= 0:
<p><strong><a href="/pokemon/buy/checkout">Proceed to checkout →</a></strong></p>
% endif
% else:
<p>Your bank balance: $${request.user.money}</p>
% endif

<h1>Browse</h1>
<form action="/pokemon/buy" method="POST">
${t.pokemon_form_table(
    *((p.default_form for p in rarity.pokemon_species) for rarity in rarities),
    subheaders=['{} (${})'.format(label, rarity.price) for label, rarity in zip(rarity_labels, rarities)],
    species_name=True,
    extra_left_cols=[{'col': add_to_cart_col, 'th': t.empty_header, 'td': add_to_cart_cell}]
)}
</form>
