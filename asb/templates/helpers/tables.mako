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

# KOs
<%def name="ko_col()"><col class="stat"></%def>
<%def name="ko_header()"><th>KOs</th></%def>
<%def name="ko_cell(pokemon)">
% if pokemon.kos:
<td class="stat">${pokemon.kos}</td>
% else:
<td></td>
% endif
</%def>

# The actual table function
<%def name="pokemon_table(*pokemon_lists, subheader_colspan=10,
    subheaders=None, extra_left_cols=[], skip_cols=[], extra_right_cols=[],
    highlight_condition=None, link_subheaders=False)">\
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
    % if link_subheaders:
    <td colspan="${subheader_colspan}">${h.link(subheader)}</td>
    % else:
    <td colspan="${subheader_colspan}">${subheader}</td>
    % endif
</tr>
% endif

% for a_pokemon in pokemon:
% if highlight_condition and highlight_condition(a_pokemon):
<tr class="highlight-row">
% else:
<tr>
% endif
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
<%def name="move_table(moves, skip_type=False)">
<% from asb.markdown import md, chomp %>\
<table class="standard-table effect-table">
<col class="move">
% if not skip_type:
<col class="type-col">
% endif
<col class="damage-class-col">
<col class="percentage">
<col class="percentage">
<col class="percentage">
<col class="stat">
<col class="summary">
<thead>
<tr>
    <th>Move</th>
    % if not skip_type:
    <th>Type</th>
    % endif
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

    % if not skip_type:
    <td class="type-cell">${h.type_icon(move.type)}</td>
    % endif

    <td class="damage-class-cell">${h.damage_class_icon(move.damage_class)}</td>

    % if move.damage is not None:
    <td class="stat">${move.damage}%</td>
    % elif move.damage_class.identifier == 'non-damaging':
    <td class="stat">—</td>
    % else:
    <td class="stat">*</td>
    % endif

    % if move.energy == 0:
    <td class="stat">—</td>
    % elif move.energy is None:
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

    <td>${move.summary | md.convert, chomp}</td>
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
    use_species = species_name or (
        squashed_forms and
        form.species.forms_are_squashable and
        form.is_default
    )
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


### BANK TABLES
<%def name="transaction_table(transaction_groups)">
<table class="transactions">
<thead>
    <tr>
        <th>Date</th>
        <th><abbr title="Amount">Amt</abbr></th>
        <th>Link</th>
        <th>Status</th>
        <th>Processed by</th>
        <th>Notes</th>
    </tr>
</thead>
% for (header, transactions) in transaction_groups:
<tbody>
    % if header:
    <tr class="subheader-row"><td colspan="6">${header}</td></tr>
    % endif

    % for transaction in transactions:
    <tr>
        % if transaction.date is None:
        <td>???</td>
        % else:
        <td>${transaction.date.strftime('%d %b')}</td>
        % endif

        % if transaction.amount >= 0:
        <td class="price">$${transaction.amount}</td>
        % else:
        <td class="price">−$${-transaction.amount}</td>
        % endif

        <td>
            % if transaction.tcod_post_id is not None:
            <a href="${transaction.link}">Post #${transaction.tcod_post_id}</a>
            % endif
        </td>

        % if transaction.state == 'from-mod':
        <td>From mod</td>
        % else:
        <td>${transaction.state.capitalize()}</td>
        % endif

        <td>
            % if transaction.approver is not None:
            ${h.link(transaction.approver)}
            % endif
        </td>

        <td class="notes">
            <ul>
                % for note in transaction.notes:
                % if note.trainer is None:
                <li>??? said: ${note.note}</li>
                % elif note.trainer == request.user:
                <li>You said: ${note.note}</li>
                % else:
                <li>${note.trainer.name} said: ${note.note}</li>
                % endif
                % endfor
            </ul>
        </td>
    </tr>
    % endfor
</tbody>
% endfor
</table>
</%def>

### BATTLE TABLES
<%def name="battle_table(*battle_lists, subheaders=None, show_end=False)">
<%
    subheader_colspan = 3
    if subheaders is None:
        subheaders = [None] * len(battle_lists)
%>
<table class="battle-table">
<thead>
<tr>
    <th>Battle</th>
    <th>Ref</th>
    <th>Started</th>
    % if show_end:
    <th>Ended</th>
    <% subheader_colspan = 4 %>\
    % endif
</tr>
</thead>

% for battles, subheader in zip(battle_lists, subheaders):
% if battles:
<tbody>
% if subheader is not None:
<tr class="subheader-row">
    <td colspan="${subheader_colspan}">${subheader}</td>
</tr>
% endif
% for battle in battles:
    <tr>
        <td class="focus-column">${h.link(battle)}</td>

        % if battle.ref is None:
        <td>???</td>
        % else:
        <td>${h.link(battle.ref)}</td>
        % endif

        <td>${battle.start_date.strftime('%Y %B %d')}</td>

        % if show_end:
        <td>
            % if battle.end_date:
            ${battle.end_date.strftime('%Y %B %d')}
            % endif
        </td>
        % endif
    </tr>
    % endfor
</tbody>
% endif
% endfor
</table>
</%def>
