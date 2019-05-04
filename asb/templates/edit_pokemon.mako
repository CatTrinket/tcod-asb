<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="markup" file="/helpers/markup.mako"/>\
<%block name='title'>Edit ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${pokemon.name}</h1>

<form method="POST">
${form.csrf_token()}
${h.form_error_list(form.csrf_token.errors)}

<fieldset>
<legend>Basics</legend>
<dl>
    <dt>${form.name.label()}</dt>
    <dd>${form.name(maxlength=30)}</dd>
    % for error in form.name.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    % if form.form is not None:
    <dt>${form.form.label()}</dt>
    <dd>${form.form()}</dd>

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
</fieldset>

<fieldset class="editor">
    <legend id="profile">Profile</legend>
    ${markup.markup_editor(form.profile, form.profile_format)}
    <p>${form.profile_preview(formaction='#profile')}</p>
</fieldset>

% if form.profile_preview.data:
    <fieldset>
        <legend>Preview</legend>
        ${markup.markup(form.profile.data, form.profile_format.data)}
    </fieldset>
% endif

<p>${form.save()}</p>
</form>
