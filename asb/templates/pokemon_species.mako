<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<dl>
    <dt>#${pokemon.species.number}</dt>
    <dd>${pokemon.name} ${h.pokemon_form_icon(pokemon)}</dd>

    <dt>Type</dt>
    <dd>
        ${h.type_icon(pokemon.types[0])}
        % if len(pokemon.types) == 2:
            ${h.type_icon(pokemon.types[1])}
        % endif
    </dd>

    % if pokemon.species.rarity is not None:
    <dt>Rarity</dt>
    <dd>
        ${pokemon.species.rarity_id}
        ($${pokemon.species.rarity.price})
    </dd>
    % endif

    <dt>Population</dt>
    <dd><a href="#census">${len(census)}</a></dd>
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
    <dt>${h.link(regular_abilities[0])}</dt>
    <dd>${regular_abilities[0].description}</dd>

    % if len(regular_abilities) == 2 and regular_abilities[1] != regular_abilities[0]:
        <dt>${h.link(regular_abilities[1])}</dt>
        <dd>${regular_abilities[1].description}</dd>
    % endif

    % if hidden_abilities and hidden_abilities[0] != regular_abilities[0]:
        <dt class="hidden-ability">${h.link(hidden_abilities[0])}</dt>
        <dd>${hidden_abilities[0].description}</dd>
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
            methods.append('{} happiness'.format(evolution_method.happiness));

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
        <td colspan="${colspan}" class="${'focus' if current else ''}">
            % if current:
            ${h.pokemon_form_icon(pokemon)}${evo.name}
            % else:
            ${h.pokemon_form_icon(evo.default_form)}${h.link(evo.default_form, text=evo.name)}
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
${t.move_table(pokemon.moves)}

<h1 id="census">${pokemon.name} in the league</h1>
${t.pokemon_table(census, skip_cols=['species'])}
