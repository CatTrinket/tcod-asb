<%def name="pokemon_table(pokemon, skip_cols=[])">\
<%
  pokemon_table_columns = [
      ('name', 'Name', None),
      ('species', 'Species', None),
      ('gender', '⚥', 'Gender'),
      ('trainer', 'Trainer', None),
      ('ability', 'Ability', None),
      ('experience', 'XP', 'Experience'),
      ('happiness', ':3', 'Happiness'),
      ('item', 'Item', None)
  ]
%>
<table>
<thead>
<tr>
    % for column, header, title in pokemon_table_columns:
    % if column not in skip_cols:
    % if title is not None:
    <th><abbr title="${title}">${header}</abbr></th>
    % else:
    <th>${header}</th>
    % endif
    % endif
    % endfor
</tr>
</thead>

<tbody>
% for p in pokemon:
<tr>
    % if 'name' not in skip_cols:
    <td class='focus-column'>
        <a href="/pokemon/${p.identifier}">${p.name}</a>
    </td>
    % endif

    % if 'species' not in skip_cols:
    <td>
        <a href="/pokemon/species/${p.species.identifier}">${p.species.name}</a>
    </td>
    % endif

    % if 'gender' not in skip_cols:
    <td class="gender">${gender_symbol(p.gender)}</td>
    % endif

    % if 'trainer' not in skip_cols:
    <td><a href="/trainers/${p.trainer.identifier}">${p.trainer.name}</a></td>
    % endif

    % if 'ability' not in skip_cols:
    <td>${p.ability.name}</td>
    % endif

    % if 'experience' not in skip_cols:
    <td class="stat">${p.experience | n, str}</td>
    % endif

    % if 'happiness' not in skip_cols:
    <td class="stat">${p.happiness | n, str}</td>
    % endif

    % if 'item' not in skip_cols:
    <td>
        % if p.item:
        <a href="/items/${p.item.identifier}">${p.item.name}</a>
        % endif
    </td>
    % endif
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
