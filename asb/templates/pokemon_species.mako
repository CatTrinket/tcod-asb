<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}</h1>

<dl>
    <dt>#${pokemon.species.number}</dt>
    <dd>${pokemon.name}</dd>

    <dt>Type</dt>
    <dd>
        ${helpers.type_icon(pokemon.types[0])}
        % if len(pokemon.types) == 2:
            &nbsp;${helpers.type_icon(pokemon.types[1])}
        % endif
    </dd>

    <%
        regular_abilities = []
        hidden_abilities = []

        for ability in pokemon.abilities:
            if ability.is_hidden:
                hidden_abilities.append(ability.ability)
            else:
                regular_abilities.append(ability.ability)
    %>

    <dt>${"Ability" if len(regular_abilities) == 1 else "Abilities"}</dt>
    <dd>${", ".join(ability.name for ability in regular_abilities)}</dd>

    % if len(pokemon.abilities) > 1:
        <dt>Hidden Ability</dt>
        <dd>${", ".join(ability.name for ability in hidden_abilities)}</dd>
    % endif
</dl>

<h1>Moves</h1>
${helpers.move_table(pokemon.moves)}
