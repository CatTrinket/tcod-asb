<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers.mako"/>\
<%block name='title'>Buy Pokémon - The Cave of Dragonflies ASB</%block>\
<%
    rarity_labels = {
        1: 'Rarity One',
        2: 'Rarity Two',
        3: 'Rarity Three',
        4: 'Rarity Four',
        5: 'Rarity Five',
        6: 'Rarity Six',
        7: 'Rarity Seven',
        8: 'Rarity Eight'
    }
%>

<%def name="add_to_cart_header()">
<th></th>
</%def>

<%def name="add_to_cart_column(pokemon)">
<td class="input"><button name="add" value="${pokemon.species.identifier}">+</button></td>
</%def>

<form action="/pokemon/buy" method="POST">
${quick_buy.csrf_token() | n}
<p>
    Quick buy: ${quick_buy.pokemon(placeholder='Enter a Pokémon') | n}
    ${quick_buy.quickbuy() | n}
</p>
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
<table>
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
    <td class="price">$${pokemon.rarity.price | n, str}</td>
  </tr>
  <% total += pokemon.rarity.price %>
  % endfor
</tbody>
<tfoot>
  <tr>
    <td colspan="3" class="focus-column">Total</td>
    <td class="price">$${total | n, str}</td>
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
<p>Your bank balance: $${request.user.money | n, str}</p>
% endif

<form action="/pokemon/buy" method="POST">
% for rarity in rarities:
<h1>${rarity_labels[rarity.id]} ($${rarity.price | n, str})</h1>
${h.pokemon_form_table(
    (p.default_form for p in rarity.pokemon_species),
    species_name=True,
    extra_left_cols=[(add_to_cart_header, add_to_cart_column)]
)}
% endfor
</form>
