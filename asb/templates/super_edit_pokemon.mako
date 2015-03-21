<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>SUPER edit ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${pokemon.name}</h1>

<form action="super-edit" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<dl>
    <dt>${form.experience.label()}</dt>
    <dd>${form.experience(size=1)}</dd>
    % for error in form.experience.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.happiness.label()}</dt>
    <dd>${form.happiness(size=1)}</dd>
    % for error in form.happiness.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    % if form.unlocked_evolutions is not None:
    <dt>${form.unlocked_evolutions.label()}</dt>
    <dd>${form.unlocked_evolutions()}</dd>
    % for error in form.unlocked_evolutions.errors:
    <dd class="form-error">${error}</dd>
    % endfor
    % endif

    <dt>${form.give_to.label}</dt>
    <dd>${form.give_to}</dd>
    % for error in form.give_to.errors:
    <dd class="form-error">${error}</dd>
    % endfor
</dl>

${form.save() | n}
</form>
