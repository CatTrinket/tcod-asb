<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Edit ${trainer.name} - Trainers - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${trainer.name}</h1>

<form action="${request.path}" method="POST">
    ${form.csrf_token()}
    ${h.form_error_list(form.csrf_token.errors)}

    <fieldset>
        <legend>Basics</legend>

        <dl>
            <dt>${form.roles.label}</dt>
            <dd>${form.roles(class_='option-list')}</dd>
            % for error in form.roles.errors:
            <dd class="form-error">${error}</dd>
            % endfor
        </dl>
    </fieldset>

    <fieldset>
        <legend>Items</legend>

        <dl>
            <dt>Move item</dt>
            <dd>Move one ${form.move_item} to ${form.item_recipient}</dd>
            % for error in form.move_item.errors + form.item_recipient.errors:
            <dd class="form-error">${error}</dd>
            % endfor

            <dt>Give item</dt>
            <dd>Give one ${form.give_item}</dd>
            % for error in form.give_item.errors:
            <dd class="form-error">${error}</dd>
            % endfor
        </dl>
    </fieldset>

    <fieldset>
        <legend>Money</legend>

        <dl>
            <dt>Current balance</dt>
            <dd>$${trainer.money}</dd>

            <dt>Add/subtract</dt>
            <dd>
                +$${form.money_add(size=2, maxlength=3)} or
                −$${form.money_subtract(size=2, maxlength=3)}
            </dd>
            % for error in form.money_add.errors + form.money_subtract.errors:
            <dd class="form-error">${error}</dd>
            % endfor

            <dt>${form.money_note.label}</dt>
            <dd>${form.money_note(size=60)}</dd>
            % for error in form.money_note.errors:
            <dd class="form-error">${error}</dd>
            % endfor
        </dl>
    </fieldset>

    ${form.save}
</form>

<h1>Danger zone</h1>

<form action="${request.path}" method="POST">
    <fieldset>
        <legend>Reset password</legend>

        ${h.form_error_list(*password_form.errors.values())}

        <p>${password_form.confirm.label} ${password_form.confirm}</p>

        ${password_form.csrf_token}
        ${password_form.reset}
    </fieldset>
</form>

<form action="${request.path}" method="POST">
    <fieldset>
        <legend>Ban</legend>

        ${h.form_error_list(*ban_form.errors.values())}

        <dl>
            <dt>Confirm</dt>
            <dd>Yes, I want to ban this user ${ban_form.confirm}</dd>

            <dt>${ban_form.reason.label}</dt>
            <dd>${ban_form.reason(size=60)}</dd>
        </dl>

        ${ban_form.csrf_token}
        ${ban_form.ban}
    </fieldset>
<form>
