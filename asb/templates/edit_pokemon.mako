<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Edit ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${pokemon.name}</h1>

<form action="edit" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<dl>
    <dt>${form.name.label() | n}</dt>
    <dd>${form.name(maxlength=30) | n}</dd>
    % for error in form.name.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    % if form.form is not None:
    <dt>${form.form.label() | n}</dt>
    <dd>${form.form() | n}</dd>

    % if pokemon.form_uncertain:
    <dd class="warning">Once ${pokemon.species.name}'s form has been set, it
    cannot be changed.</dd>
    % endif

    % for error in form.form.errors:
    <dd class="form-error">${error}</dd>
    % endfor
    % endif

    <dt>${form.color.label()}</dt>
    <dd>
        <ul class="option-list" id="pokemon-color-list">
            % for color in form.color:
            <li>
                <label>
                    ${color} ${color.label.text}
                    ${h.pokemon_form_sprite(pokemon.form, gender=pokemon.gender,
                                            shiny=color.label.text == 'Shiny')}
                </label>
            </li>
            % endfor
        </ul>
    </dd>
</dl>

${form.save() | n}
</form>
