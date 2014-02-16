<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<dl>
    <dt>#${pokemon.species.number}</dt>
    <dd>${pokemon.name} &nbsp; ${helpers.pokemon_form_icon(pokemon)}</dd>

    <dt>Type</dt>
    <dd>
        ${helpers.type_icon(pokemon.types[0])}
        % if len(pokemon.types) == 2:
            &nbsp;${helpers.type_icon(pokemon.types[1])}
        % endif
    </dd>

    <dt>Rarity</dt>
    <dd>???</dd>

    <dt>Price</dt>
    <dd>???</dd>

    <dt>Population</dt>
    <dd><a>???</a></dd>
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

    % if len(regular_abilities) == 2:
        <dt>${helpers.link(regular_abilities[1])}</dt>
        <dd>${regular_abilities[1].summary}</dd>
    % endif

    % if hidden_abilities:
        <dt class="hidden-ability">${helpers.link(hidden_abilities[0])}</dt>
        <dd>${hidden_abilities[0].summary}</dd>
    % endif
</dl>

<h1>Moves</h1>
${helpers.move_table(pokemon.moves)}

<h1>Population</h1>
