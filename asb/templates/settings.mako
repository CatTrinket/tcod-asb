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

<h1>Reset/delete account</h1>
<form action="/settings" method="POST">
    ${reset_delete.csrf_token() | n}
    ${h.form_error_list(reset_delete.csrf_token.errors)}

    <p>If you reset or delete your account, all your stuff will disappear and
    your Pokémon will be released into the wild, i.e. deleted.  <strong>There
    is absolutely no way they can be recovered.</strong></p>

    <p>If you really want to reset or delete your account, copy out the
    sentence below.  <strong>There is no confirmation after this.</strong></p>

    <p><em>${reset_delete.confirmation}</em></p>

    <p>Sentence: ${reset_delete.i_understand(size=60) | n}</p>
    <p>Password: ${reset_delete.reset_pass(autocomplete='off') | n}</p>

    ${h.form_error_list(reset_delete.i_understand.errors +
        reset_delete.reset_pass.errors)}

    <p>${reset_delete.reset() | n} ${reset_delete.delete() | n}</p>
</form>
