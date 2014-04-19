<%def name="link(db_resource, text=None, **kwargs)">\
## resource_url will add a trailing slash unless we do it this way
<a href="${request.resource_url(db_resource.__parent__,
    db_resource.__name__, **kwargs)}">${text or db_resource.name}</a>\
</%def>

<%def name="num(n, invisible_plus=True)">\
% if n < 0:
−${n * -1 | n, str}\
% elif n == 0 or invisible_plus:
${n | n, str}\
% else:
+${n | n, str}\
% endif
</%def>

<%def name="type_icon(type)">\
<span class="type type-${type.identifier}">${type.name}</span>\
</%def>

<%def name="damage_class_icon(damage_class)">\
<span class="damage-class damage-class-${damage_class.identifier}">\
% if damage_class.identifier == 'non-damaging':
—\
% else:
${damage_class.name.capitalize()}\
% endif
</span>\
</%def>

<%def name="name_header()">
<th colspan="2">Name</th>
</%def>

<%def name="name_cell(pokemon)">
<td class="icon">${pokemon_form_icon(pokemon.form,
    gender=pokemon.gender.identifier)}</td>
<td class="focus-column">${link(pokemon)}</td>
</%def>

<%def name="species_header()">
<th>Species</th>
</%def>

<%def name="species_cell(pokemon)">
<td>${link(pokemon.form, text=pokemon.species.name)}</td>
</%def>

<%def name="gender_header()">
<th><abbr title="Gender">⚥</abbr></th>
</%def>

<%def name="gender_cell(pokemon)">
<td class="gender">${gender_symbol(pokemon.gender)}</td>
</%def>

<%def name="trainer_header()">
<th>Trainer</th>
</%def>

<%def name="trainer_cell(pokemon)">
<td>${link(pokemon.trainer)}
</%def>

<%def name="ability_header()">
<th>Ability</th>
</%def>

<%def name="ability_cell(pokemon)">
<td>${link(pokemon.ability)}</td>
</%def>

<%def name="experience_header()">
<th><abbr title="Experience">XP</abbr></th>
</%def>

<%def name="experience_cell(pokemon)">
<td class="stat">${pokemon.experience | n, str}</td>
</%def>

<%def name="happiness_header()">
<th><abbr title="Happiness">:3</abbr></th>
</%def>

<%def name="happiness_cell(pokemon)">
<td class="stat">${pokemon.happiness | n, str}</td>
</%def>

<%def name="item_header()">
<th colspan="2">Item</th>
</%def>

<%def name="item_cell(pokemon)">
% if pokemon.item is not None:
<td class="icon"><img src="/static/images/items/${pokemon.item.identifier}.png"></td>
<td>${link(pokemon.item)}</td>
% else:
<td colspan="2"></td>
% endif
</%def>

<%def name="pokemon_table(pokemon, skip_cols=[], extra_left_cols=[],
    extra_right_cols=[])">\
<%
  columns = []

  columns.extend(extra_left_cols)

  columns.extend((header_func, cell_func) for name, header_func, cell_func in [
      ('name', name_header, name_cell),
      ('gender', gender_header, gender_cell),
      ('species', species_header, species_cell),
      ('trainer', trainer_header, trainer_cell),
      ('ability', ability_header, ability_cell),
      ('experience', experience_header, experience_cell),
      ('happiness', happiness_header, happiness_cell),
      ('item', item_header, item_cell)
  ] if name not in skip_cols)

  columns.extend(extra_right_cols)
%>
<table>
<thead>
<tr>
    % for header_func, cell_func in columns:
    ${header_func()}
    % endfor
</tr>
</thead>

<tbody>
% for p in pokemon:
<tr>
    % for header_func, cell_func in columns:
    ${cell_func(p)}
    % endfor
</tr>
% endfor
</table>
</%def>

<%def name="move_table(moves)">
<table class="effect-table">
<thead>
<tr>
    <th>Move</th>
    <th>Type</th>
    <th>Stat</th>
    <th><abbr title="Base damage">Dmg</abbr></th>
    <th><abbr title="Base energy cost">En.</abbr></th>
    <th><abbr title="Accuracy">Acc.</abbr></th>
    <th>Summary</th>
</tr>
</thead>

<tbody>
% for move in moves:
<tr>
    <td class="focus-column"><a href="/moves/${move.identifier}">${move.name}</a></td>

    <td class="type-cell">${type_icon(move.type)}</td>

    <td class="damage-class-cell">${damage_class_icon(move.damage_class)}</td>

    % if move.damage is None:
    <td class="stat">—</td>
    % elif move.damage == -1:
    <td class="stat">*</td>
    % else:
    <td class="stat">${move.damage | n, str}%</td>
    % endif

    % if move.energy is None:
    <td class="stat">—</td>
    % elif move.energy == -1:
    <td class="stat">*</td>
    % elif move.energy == 0:
    <td class="stat">?</td>
    % else:
    <td class="stat">${move.energy | n, str}%</td>
    % endif

    % if move.accuracy is None:
    <td class="stat">—</td>
    % else:
    <td class="stat">${move.accuracy | n, str}%</td>
    % endif

    <td>${move.summary}</td>
</tr>
% endfor
</tbody>
</table>
</%def>

<%def name="pokemon_form_table(*form_lists, **kwargs)">
<%
  # Temporary fix until Mako can handle Python 3's AST
  species_name = kwargs.pop('species_name', False)
  squashed_forms = kwargs.pop('squashed_forms', False)
  extra_left_cols = kwargs.pop('extra_left_cols', [])
  extra_right_cols = kwargs.pop('extra_right_cols', [])
  subheaders = kwargs.pop('subheaders', None)

  if subheaders is not None:
      sections = zip(subheaders, form_lists)
  else:
      sections = [(None, forms) for forms in form_lists]
%>
<table>
<thead>
<tr>
    % for header_func, cell_func in extra_left_cols:
    ${header_func()}
    % endfor
    <th colspan="2">Pokémon</th>
    <th>Type</th>
    <th>Ability 1</th>
    <th>Ability 2</th>
    <th>Hidden Ability</th>
    % for header_func, cell_func in extra_right_cols:
    ${header_func()}
    % endfor
</tr>
</thead>
% for subheader, forms in sections:
% if forms:
<tbody>
% if subheader is not None:
<!-- I know this is incorrect, but colspan="0" doesn't work in Chrome and I
really don't want to calculate the colspan manually. I'm sorry. -->
<tr class="subheader-row"><td colspan="1000">${subheader}</td></tr>
% endif

% for form in forms:
<%
    use_species = (species_name or (squashed_forms and
        form.species.forms_are_squashable))
    name_override = form.species.name if use_species else None

    abilities = [None, None, None]
    for ability in form.abilities:
        abilities[ability.slot - 1] = ability
%>
<tr>
    % for header_func, cell_func in extra_left_cols:
    ${cell_func(form)}
    % endfor

    <td class="icon">${pokemon_form_icon(form)}</td>
    <td class="focus-column">${link(form, text=name_override)}</td>

    <td class="type-cell">\
% for type in form.types:
${type_icon(type)}\
% endfor
</td>

    % for ability in abilities:
    % if ability is None:
    <td></td>
    % elif ability.is_hidden:
    <td class="hidden-ability">${link(ability.ability)}</td>
    % else:
    <td>${link(ability.ability)}</td>
    % endif
    % endfor

    % for header_func, cell_func in extra_right_cols:
    ${cell_func(form)}
    % endfor
</tr>
% endfor
</tbody>
% endif
% endfor
</table>
</%def>

<%def name="pokemon_form_icon(form, gender=None)">\
<%
    if gender is not None and form.identifier in ['unfezant', 'frillish',
      'jellicent', 'pyroar']:
        # Meowstic's genders are forms, so that's already in the identifier
        filename = '{}-{}.png'.format(form.identifier, gender)
    else:
        filename = '{}.png'.format(form.identifier)
%>\
<img src="/static/images/pokemon-icons/${filename}" alt="">\
</%def>

<%def name="pokemon_form_sprite(form, gender=None)">\
<%
   filename = '/static/images/pokemon/{}.png'.format(form.identifier)
   if gender is not None:
       from pkg_resources import resource_exists

       alt_filename = '/static/images/pokemon/{}-{}.png'.format(
           form.identifier, gender)

       if resource_exists('asb', alt_filename):
           filename = alt_filename
%>\
<img src="${filename}" alt="">\
</%def>

<%def name="gender_symbol(gender)">\
<span class="gender-symbol-${gender.identifier}">\
% if gender.identifier == 'female':
♀\
% elif gender.identifier == 'male':
♂\
% elif gender.identifier == 'genderless':
—\
% endif
</span>\
</%def>
