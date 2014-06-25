<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name="title">Settings - The Cave of Dragonflies ASB</%block>

<h1>Update username</h1>
<form action="/settings" method="POST">
    ${update_username.csrf_token() | n}
    ${h.form_error_list(update_username.csrf_token.errors)}

    <p>Update your username to match your forum profile:
    ${update_username.update_username() | n}</p>
    ${h.form_error_list(update_username.update_username.errors)}
</form>

<form action="/settings" method="POST" id="settings-form">
    ${settings.csrf_token() | n}
    ${h.form_error_list(settings.csrf_token.errors)}

    <h1>Change password</h1>
    ${settings.password.label() | n}
    ${settings.password() | n}

    ${settings.new_password.label() | n}
    ${settings.new_password() | n}

    ${settings.new_password_confirm.label() | n}
    ${settings.new_password_confirm() | n}

    ${h.form_error_list(
        settings.password.errors +
        settings.new_password.errors +
        settings.new_password_confirm.errors
    )}

    <p>${settings.save() | n}</p>
</form>
