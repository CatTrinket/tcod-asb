<%namespace name="h" file="/helpers/helpers.mako"/>

<%def name="empty_header()"><th></th></%def>
<%def name="ticky_col()"><col class="ticky"></%def>

### POKÉMON TABLES
# Column functions
# Name
<%def name="name_col()"><col class="pokemon-icon"><col class="pokemon"></%def>
<%def name="name_header()"><th colspan="2">Name</th></%def>
<%def name="name_cell(pokemon)">
<td class="icon">${h.pokemon_form_icon(
    pokemon.form,
    gender=pokemon.gender.identifier,
    alt=''
)}</td>
<td class="focus-column">${h.link(pokemon)}</td>
</%def>

# Species
<%def name="species_col()"><col class="pokemon-species"></%def>
<%def name="species_header()"><th>Species</th></%def>
<%def name="species_cell(pokemon)"><td>${h.link(pokemon.form, text=pokemon.species.name)}</td></%def>

# Gender
<%def name="gender_col()"><col class="gender"></%def>
<%def name="gender_header()"><th><abbr title="Gender">⚥</abbr></th></%def>
<%def name="gender_cell(pokemon)"><td class="gender">${h.gender_symbol(pokemon.gender)}</td></%def>

# Trainer
<%def name="trainer_col()"><col class="trainer"></%def>
<%def name="trainer_header()"><th>Trainer</th></%def>
<%def name="trainer_cell(pokemon)"><td>${h.link(pokemon.trainer)}</%def>

# Ability
<%def name="ability_col()"><col class="ability"></%def>
<%def name="ability_header()"><th>Ability</th></%def>
<%def name="ability_cell(pokemon)">
<td\
% if pokemon.ability_slot == 3:
 class="hidden-ability"\
% endif
>${h.link(pokemon.ability)}</td>
</%def>

# Experience
<%def name="experience_col()"><col class="stat"></%def>
<%def name="experience_header()"><th><abbr title="Experience">XP</abbr></th></%def>
<%def name="experience_cell(pokemon)"><td class="stat">${pokemon.experience}</td></%def>

# Happiness
<%def name="happiness_col()"><col class="stat"></%def>
<%def name="happiness_header()"><th><abbr title="Happiness">:3</abbr></th></%def>
<%def name="happiness_cell(pokemon)"><td class="stat">${pokemon.happiness}</td></%def>

# Held item
<%def name="item_col()"><col class="icon item-icon"><col class="item"></%def>
<%def name="item_header()"><th colspan="2">Item</th></%def>
<%def name="item_cell(pokemon)">
% if pokemon.item is not None:
<td class="icon">
    <img src="/static/images/items/${pokemon.item.identifier}.png" alt="">
</td>
<td>${h.link(pokemon.item)}</td>
% else:
<td colspan="2"></td>
% endif
</%def>

# The actual table function
<%def name="pokemon_table(*pokemon_lists, subheader_colspan=10,
    subheaders=None, extra_left_cols=[], skip_cols=[], extra_right_cols=[])">\
<%
  if subheaders is None:
      subheaders = [None] * len(pokemon_lists)

  columns = []
  columns.extend(extra_left_cols)
  columns.extend(funcs for name, funcs in [
      ('name', {'col': name_col, 'th': name_header, 'td': name_cell}),
      ('gender', {'col': gender_col, 'th': gender_header, 'td': gender_cell}),
      ('species', {'col': species_col, 'th': species_header, 'td': species_cell}),
      ('trainer', {'col': trainer_col, 'th': trainer_header, 'td': trainer_cell}),
      ('ability', {'col': ability_col, 'th': ability_header, 'td': ability_cell}),
      ('experience', {'col': experience_col, 'th': experience_header, 'td': experience_cell}),
      ('happiness', {'col': happiness_col, 'th': happiness_header, 'td': happiness_cell}),
      ('item', {'col': item_col, 'th': item_header, 'td': item_cell})
  ] if name not in skip_cols)
  columns.extend(extra_right_cols)
%>
<table class="standard-table">
% for column in columns:
${column['col']()}
% endfor
<thead>
<tr>
    % for column in columns:
    ${column['th']()}
    % endfor
</tr>
</thead>

% for pokemon, subheader in zip(pokemon_lists, subheaders):
% if pokemon:
<tbody>
% if subheader is not None:
<tr class="subheader-row">
    <td colspan="${subheader_colspan}">${subheader}
</tr>
% endif

% for a_pokemon in pokemon:
<tr>
    % for column in columns:
    ${column['td'](a_pokemon)}
    % endfor
</tr>
% endfor
</tbody>
% endif
% endfor
</table>
</%def>


### MOVE TABLES
# Always the same columns
<%def name="move_table(moves)">
<table class="standard-table effect-table">
<col class="move">
<col class="type-col">
<col class="damage-class-col">
<col class="percentage">
<col class="percentage">
<col class="percentage">
<col class="stat">
<col class="summary">
<thead>
<tr>
    <th>Move</th>
    <th>Type</th>
    <th>Stat</th>
    <th><abbr title="Base damage">Dmg</abbr></th>
    <th><abbr title="Base energy cost">En.</abbr></th>
    <th><abbr title="Accuracy">Acc.</abbr></th>
    <th><abbr title="Priority">Pri.</abbr></th>
    <th>Summary</th>
</tr>
</thead>

<tbody>
% for move in moves:
<tr>
    <td class="focus-column"><a href="/moves/${move.identifier}">${move.name}</a></td>

    <td class="type-cell">${h.type_icon(move.type)}</td>

    <td class="damage-class-cell">${h.damage_class_icon(move.damage_class)}</td>

    % if move.damage is not None:
    <td class="stat">${move.damage}%</td>
    % elif move.damage_class.identifier == 'non-damaging':
    <td class="stat">—</td>
    % else:
    <td class="stat">*</td>
    % endif

    % if move.energy is None:
    <td class="stat">—</td>
    % elif move.energy == -1:
    <td class="stat">*</td>
    % else:
    <td class="stat">${move.energy}%</td>
    % endif

    % if move.accuracy is None:
    <td class="stat">—</td>
    % else:
    <td class="stat">${move.accuracy}%</td>
    % endif

    % if move.priority == 0:
    <td></td>
    % else:
    <td class="stat \
${'positive' if move.priority > 0 else 'negative'}-priority\
">${h.num(move.priority, invisible_plus=False)}</td>
    % endif

    <td>${move.summary}</td>
</tr>
% endfor
</tbody>
</table>
</%def>


### POKÉMON SPECIES TABLES
<%def name="_col()">
<col>
</%def>

<%def name="pokemon_form_table(*form_lists, squashed_forms=False,
    species_name=False, extra_left_cols=[], extra_right_cols=[],
    subheaders=None, subheader_colspan=7)">
<%
    if subheaders is None:
        subheaders = [None] * len(form_lists)
%>
<table class="standard-table">
% for column in extra_left_cols:
${column.get('col', _col)()}
% endfor
<col class="pokemon-icon">
<col class="${'pokemon-species' if species_name else 'pokemon-form'}">
<col class="two-types">
<col class="ability">
<col class="ability">
<col class="ability">
<col class="stat stat-speed">
% for column in extra_right_cols:
${column.get('col', _col)()}
% endfor
<thead>
<tr>
    % for column in extra_left_cols:
    ${column['th']()}
    % endfor
    <th colspan="2">Pokémon</th>
    <th>Type</th>
    <th>Ability 1</th>
    <th>Ability 2</th>
    <th>Hidden Ability</th>
    <th>Speed</th>
    % for column in extra_right_cols:
    ${column['th']()}
    % endfor
</tr>
</thead>
% for forms, subheader in zip(form_lists, subheaders):
% if forms:
<tbody>
% if subheader is not None:
<tr class="subheader-row"><td colspan="${subheader_colspan}">${subheader}</td></tr>
% endif

% for form in forms:
<%
    use_species = (species_name or (squashed_forms and
        form.species.forms_are_squashable))
    name_override = form.species.name if use_species else None

    abilities = [(None, False), (None, False), (None, False)]
    seen_abilities = set()
    for ability in form.abilities:
        abilities[ability.slot - 1] = (ability, ability.ability_id in seen_abilities)
        seen_abilities.add(ability.ability_id)
%>
<tr>
    % for column in extra_left_cols:
    ${column['td'](form)}
    % endfor

    <td class="icon pokemon-icon">${h.pokemon_form_icon(form, alt='')}</td>
    <td class="focus-column">${h.link(form, text=name_override)}</td>

    <td class="type-cell">\
% for type in form.types:
${h.type_icon(type)}\
% endfor
</td>

    % for ability, is_redundant in abilities:
    % if ability is None:
    <td></td>
    % else:
    <td class="\
    % if is_redundant:
redundant-ability \
    % endif
    % if ability.is_hidden:
hidden-ability\
    % endif
">${h.link(ability.ability)}</td>
    % endif
    % endfor

    <td class="stat stat-speed">${form.speed}</td>

    % for column in extra_right_cols:
    ${column['td'](form)}
    % endfor
</tr>
% endfor
</tbody>
% endif
% endfor
</table>
</%def>
