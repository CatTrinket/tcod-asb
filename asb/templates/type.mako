<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${type.name} - Types - The Cave of Dragonflies ASB</%block>\

<h1>${type.name}</h1>
<h2>Attacking</h2>
<dl class="type-matchups">
    % for (result, types) in attacking_matchups.items():
    <dt>${attacking_labels[result]}</dt>
    <dd>
        % if types:
        % for other_type in types:
${h.type_icon(other_type)}\
        % endfor
        % else:
        None
        % endif
    </dd>
    % endfor
</dl>

<h2>Defending</h2>
<dl class="type-matchups">
    % for (result, types) in defending_matchups.items():
    <dt>${defending_labels[result]}</dt>
    <dd>
        % if types:
        % for other_type in types:
${h.type_icon(other_type)}\
        % endfor
        % else:
        None
        % endif
    </dd>
    % endfor
</dl>

<h1>Pokémon</h1>
${t.pokemon_form_table(pokemon, squashed_forms=True)}

<h1>Moves</h1>
${t.move_table(type.moves, skip_type=True)}
