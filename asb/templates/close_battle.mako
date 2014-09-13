<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${battle.name} - Battles - The Cave of Dragonflies ASB</%block>\

<h1>Close ${battle.name}</h1>
<form action="${request.path}" method="POST">
${form.csrf_token}
${h.form_error_list(form.csrf_token.errors)}

<p>${form.who_won.label}</p>
${form.who_won(class_='option-list')}
${h.form_error_list(form.who_won.errors)}

<p>${form.length.label}</p>
${form.length(class_='option-list')}
${h.form_error_list(form.length.errors)}

<h1>Pokémon</h1>

<p>Check off Pokémon that participated and indicate how many KOs they scored.
Experience, happiness, and prize money will be calculated from this.</p>

${h.form_error_list(form.pokemon.errors.values())}

<table>
<thead>
    <tr>
        <th colspan="3">Pokémon</th>
        <th>KOs</th>
    </tr>
</thead>

% for (trainer, squad) in form.pokemon_by_squad():
<tbody>
    <tr class="subheader-row">
        <td colspan="5">${trainer.name}</td>
    </tr>

    % for (pokemon, subform) in squad:
    <tr>
        <td class="input ticky">
            ${subform.participated}
        </td>

        <td class="icon pokemon-icon">
            ${h.pokemon_form_icon(pokemon.form, gender=pokemon.gender, alt='')}
        </td>

        <td class="focus-column">
            % if pokemon.pokemon:
            ${h.link(pokemon.pokemon, text=pokemon.name)}
            % else:
            ${pokemon.name}
            % endif
        </td>

        <td class="input">
            ${subform.kos(size=2, maxlength=2)}
        </td>
    </tr>
    % endfor
</tbody>
% endfor
</table>

${form.submit}
</form>
