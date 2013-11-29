<%def name="link(db_resource)">
## resource_url will add a trailing slash unless we do it this way
<a href="${request.resource_url(db_resource.__parent__,
    db_resource.__name__)}">${db_resource.name}</a>
</%def>

<%def name="name_header()">
<th colspan="2">Name</th>
</%def>

<%def name="name_cell(pokemon)">
<td class="icon"><img src="/static/images/pokemon-icons/${pokemon.form.species_id | str, n}.png" alt=""></td>
<td class="focus-column">${link(pokemon)}</td>
</%def>

<%def name="species_header()">
<th>Species</th>
</%def>

<%def name="species_cell(pokemon)">
<td>${link(pokemon.species.default_form)}</td>
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

  columns.extend(column for column in [
      (name_header, name_cell),
      (gender_header, gender_cell),
      (species_header, species_cell),
      (trainer_header, trainer_cell),
      (ability_header, ability_cell),
      (experience_header, experience_cell),
      (happiness_header, happiness_cell),
      (item_header, item_cell)
  ] if column not in skip_cols)

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
