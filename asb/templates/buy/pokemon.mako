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

    pokemon_buttons = iter(browse.add)
%>

<%def name="add_to_cart_col()">
<col class="input-small">
</%def>

<%def name="add_to_cart_cell(pokemon)">
<td class="input">${next(pokemon_buttons)}</td>
</%def>

<form action="/pokemon/buy" method="POST">
${quick_buy.csrf_token() | n}
Quick buy: ${quick_buy.pokemon(placeholder='Enter a Pokémon') | n}
${quick_buy.quickbuy() | n}

${h.form_error_list(quick_buy.csrf_token.errors + quick_buy.pokemon.errors)}
</form>

% if cart_species:
<% total = 0 %>
<h1>Cart</h1>
<form action="/pokemon/buy" method="POST">
${cart_form.csrf_token()}
${h.form_error_list(cart_form.csrf_token.errors)}

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
  % for (pokemon, promotion), remove in zip(cart_species, cart_form.remove):
  <tr>
    <td class="input">${remove()}</td>
    <td class="icon">${h.pokemon_form_icon(pokemon.default_form, alt='')}</td>
    <td class="focus-column">${h.link(pokemon.default_form, text=pokemon.name)}</td>
    % if promotion is None:
    <td class="price">$${pokemon.rarity.price}</td>
    <% total += pokemon.rarity.price %>
    % else:
    <td class="price promotion-price">$${promotion.price}</td>
    <% total += promotion.price %>
    % endif
  </tr>
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

% for (promotion, form) in promotions:
<% promotion_buttons = iter(form.add) %>
<%def name="promotion_add_to_cart_cell(pokemon)">
<td class="input">${next(promotion_buttons)}</td>
</%def>

<h1>${promotion.name}</h1>
<form action="/pokemon/buy" method="POST">
${form.csrf_token()}
${h.form_error_list(form.csrf_token.errors)}

${t.pokemon_form_table(
    (p.default_form for p in promotion.pokemon_species),
    species_name=True,
    extra_left_cols=[{
        'col': add_to_cart_col,
        'th': t.empty_header,
        'td': promotion_add_to_cart_cell
    }]
)}
</form>
% endfor

<h1>Browse</h1>
<form action="/pokemon/buy" method="POST">
${browse.csrf_token()}
${h.form_error_list(browse.csrf_token.errors)}

${t.pokemon_form_table(
    *((p.default_form for p in rarity.pokemon_species) for rarity in rarities),
    species_name=True,
    subheaders=[
        '{} (${})'.format(label, rarity.price)
        for label, rarity in zip(rarity_labels, rarities)
    ],
    extra_left_cols=[{
        'col': add_to_cart_col,
        'th': t.empty_header,
        'td': add_to_cart_cell
    }]
)}
</form>
