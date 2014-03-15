<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<dl>
    <dt>#${pokemon.species.number}</dt>
    <dd>${pokemon.name} ${helpers.pokemon_form_icon(pokemon)}</dd>

    <dt>Type</dt>
    <dd>
        ${helpers.type_icon(pokemon.types[0])}
        % if len(pokemon.types) == 2:
            ${helpers.type_icon(pokemon.types[1])}
        % endif
    </dd>

    <dt>Rarity</dt>
    <dd>
        % if pokemon.species.rarity_id is not None:
            ${pokemon.species.rarity_id | n, str}
        % else:
            Too rare for you.
        % endif
    </dd>

    <dt>Price</dt>
    <dd>
        % if pokemon.species.rarity is not None:
            $${pokemon.species.rarity.price | n, str}
        % else:
            Unbuyable
        % endif
    </dd>

    <dt>Population</dt>
    <dd><a href="#census">${len(pokemon.pokemon) | n, str}</a></dd>
</dl>

<h2>${"Ability" if len(pokemon.abilities) == 1 else "Abilities"}</h2>

    <%
        regular_abilities = []
        hidden_abilities = []

        for ability in pokemon.abilities:
            if ability.is_hidden:
                hidden_abilities.append(ability.ability)
            else:
                regular_abilities.append(ability.ability)
    %>

<dl>
    <dt>${helpers.link(regular_abilities[0])}</dt>
    <dd>${regular_abilities[0].summary}</dd>

    % if len(regular_abilities) == 2 and regular_abilities[1] != regular_abilities[0]:
        <dt>${helpers.link(regular_abilities[1])}</dt>
        <dd>${regular_abilities[1].summary}</dd>
    % endif

    % if hidden_abilities and hidden_abilities[0] != regular_abilities[0]:
        <dt class="hidden-ability">${helpers.link(hidden_abilities[0])}</dt>
        <dd>${hidden_abilities[0].summary}</dd>
    % endif
</dl>

<h1>Evolution</h1>

<%
    def format_evolution_method(pokemon):
        evolution_method = pokemon.evolution_method
        if evolution_method is None:
            return ''

        methods = []
        if evolution_method.item_id is not None:
            methods.append('battle holding {} {}'.format(
                'an' if evolution_method.item.name[0].lower() in 'aeiou'
                     else 'a',
                evolution_method.item.name))
        if evolution_method.experience is not None:
            methods.append('{} EXP'.format(evolution_method.experience))
        if evolution_method.happiness is not None:
            methods.append('4 happiness');

        methods = [", with ".join(methods)]
        if evolution_method.buyable_price is not None:
            methods.append('pay ${}'.format(evolution_method.buyable_price))
        if evolution_method.can_trade_instead:
            methods.append('trade');

        methods = " <em>OR</em> ".join(methods)
        if evolution_method.gender_id is not None:
            methods += ' ({} only)'.format(evolution_method.gender.name)

        return methods
%>

<table class="evolution-tree">
    % for layer in evo_tree:
    <tr>
        % for evo, colspan in layer:
        <% current = evo == pokemon.species %>
        <td colspan="${colspan | n, str}" class="${'focus' if current else ''}">
            % if current:
            ${helpers.pokemon_form_icon(pokemon)}${evo.name}
            % else:
            ${helpers.pokemon_form_icon(evo.default_form)}${helpers.link(evo.default_form, text=evo.name)}
            % endif
            % if evo.evolution_method is not None:
            <p class="evolution-method">${format_evolution_method(evo) | n}</p>
            % endif
        </td>
        % endfor
    </tr>
    % endfor
</table>

<h1>Moves</h1>
${helpers.move_table(pokemon.moves)}

<h1><a name="census">Population</a></h1>

${helpers.pokemon_table(pokemon.pokemon, skip_cols=['species'])}
