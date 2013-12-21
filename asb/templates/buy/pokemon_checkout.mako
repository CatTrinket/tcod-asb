<%inherit file='/base.mako'/>\
<%block name='title'>Buy Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Checkout</h1>

<form action="/pokemon/buy/checkout" method="POST">
% if form.csrf_token.errors:
<ul class="form-error">
    % for error in form.csrf_token.errors:
    <li>${error}</li>
    % endfor
</ul>
% endif
${form.csrf_token | n, str}

% for subform in form.pokemon:
<h2>${subform.species.name}\
</h2>
<dl>
    <dt>${subform.name_.label() | n}</dt>
    <dd>${subform.name_() | n}</dd>

    % if hasattr(subform.form, 'gender'):
    <dt>${subform.gender.label() | n}</dt>
    <dd>${subform.gender() | n}</dd>
    % else:
    <dt>Gender</dt>
    <dd>${subform.species.genders[0].name.capitalize()}</dd>
    % endif

    % if hasattr(subform.form, 'ability'):
    <dt>${subform.ability.label() | n}</dt>
    <dd>${subform.ability() | n}</dd>
    % else:
    <dt>Ability</dt>
    <dd>${subform.species.default_form.abilities[0].ability.name}</dd>
    % endif

    % if hasattr(subform.form, 'form_'):
    <dt>${subform.form_.label() | n}</dt>
    <dd>${subform.form_() | n}</dd>
    % endif
</dl>

% if subform.errors:
<ul class="form-error">
    % for field, errors in subform.errors.items():
    % for error in errors:
    <li>${field.capitalize()}: ${error}</li>
    % endfor
    % endfor
</ul>
% endif
% endfor

${form.submit | n, str}
</form>
