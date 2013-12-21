<%inherit file='/base.mako'/>\
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

<form action="/pokemon/buy" method="POST">
${quick_buy.csrf_token() | n}
<p>
    Quick buy: ${quick_buy.pokemon(placeholder='Enter a Pokémon') | n}
    <button type="submit">Go!</button>
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

% for rarity in rarities:
<h1>${rarity_labels[rarity.id]} ($${rarity.price | n, str})</h1>
<table>
<thead>
    <tr><th>Name</th></tr>
</thead>
<tbody>
    % for pokemon in (p for p in rarity.pokemon_species if p.id < 10000):
    <tr><td>${pokemon.name}</td></tr>
    % endfor
</tbody>
</table>
% endfor
