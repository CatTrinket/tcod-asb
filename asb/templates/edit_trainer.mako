<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Edit ${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${trainer.name}</h1>

<form action="edit" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<dl>
    <dt>${form.money_add.label}</dt>
    <dd>$${trainer.money} + $${form.money_add(size=2)}</dt>
    % for error in form.money_add.errors:
    <dd class="form-error">${error}</dd>
    % endfor
</dl>

${form.save() | n}
</form>
