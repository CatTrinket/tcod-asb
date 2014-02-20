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
    evolution_tree = {'basic': None, 'stage1': [], 'stage2': []}

    if pokemon.species.pre_evolution is None:
        evolution_tree['basic'] = pokemon.species

    elif pokemon.species.pre_evolution.pre_evolution is None:
        evolution_tree['basic'] = pokemon.species.pre_evolution

    else:
        evolution_tree['basic'] = pokemon.species.pre_evolution.pre_evolution

    evolution_tree['stage1'] = evolution_tree['basic'].evolutions
    evolution_tree['stage2'] = [evolution.evolutions
        for evolution in evolution_tree['stage1']]

    num_basic = 1
    num_stage1 = len(evolution_tree['stage1'])
    num_stage2 = sum(len(evolutions) for evolutions in evolution_tree['stage2'])

    basic = evolution_tree['basic']
    stage1_row = '<tr>'
    stage2_row = '<tr>'

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

        return '<p class="evolution-method">{}</p>'.format(methods)

    def format_cell(colspan, evolution):
        cell_template = \
            '''<td colspan="{}"{}>''' \
            '''<img src="/static/images/pokemon-icons/{}.png" alt="">''' \
            '''<a href="{}">{}</a>''' \
            '''{}''' \
            '''</td>'''

        form = evolution.default_form

        return cell_template.format(
            colspan,
            ' class="focus"' if evolution.id == pokemon.species_id else '',
            form.identifier,
            form.identifier,
            evolution.name,
            format_evolution_method(evolution))

    for evolution in evolution_tree['stage1']:
        stage1_row += format_cell(max(1, len(evolution.evolutions)), evolution)
    stage1_row += '</tr>'

    for evolutions in evolution_tree['stage2']:
        for evolution in evolutions:
            stage2_row += format_cell(1, evolution)
    stage2_row += '</tr>'
%>

<table class="evolution-tree">
    <tr>
        ${format_cell(max(num_basic, num_stage1, num_stage2), basic) | n}
    </tr>

    % if num_stage1:
        ${stage1_row | n}
    % endif

    % if num_stage2:
        ${stage2_row | n}
    % endif
</table>

<h1>Moves</h1>
${helpers.move_table(pokemon.moves)}

<h1><a name="census">Population</a></h1>

${helpers.pokemon_table(pokemon.pokemon, skip_cols=['species'])}
