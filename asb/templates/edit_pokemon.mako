<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Edit ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${pokemon.name}</h1>

<form action="edit" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<!-- XXX This shouldn't really be a dl -->
<dl>
    <dt>${form.name.label() | n}</dt>
    <dd>${form.name() | n}</dd>
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
</dl>

${form.save() | n}
</form>
