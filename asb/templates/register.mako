<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name="title">Register - The Cave of Dragonflies ASB</%block>
<form action="/register" method="POST" id="registration-form">
    ${form.csrf_token() | n}
    ${h.form_error_list(form.csrf_token.errors)}


    ${form.username.label() | n}
    ${form.username(maxlength=30) | n}
    ${h.form_error_list(form.username.errors)}

    <p>Note that creating multiple accounts to play the game is considered
    cheating, and anyone caught doing so will be banned from ASB.</p>


    <hr>


    ${form.password.label() | n}
    ${form.password() | n}

    ${form.password_confirm.label() | n}
    ${form.password_confirm() | n}

    ${h.form_error_list(form.password.errors, form.password_confirm.errors)}

    <p>This is separate from your forum password.  While we don't encourage
    reusing passwords, nobody can see your password either way.</p>


    <hr>


    ${form.email.label() | n}
    ${form.email() | n}

    <p>This will be used to reset your password if you forget it.</p>


    <p>${form.submit() | n}</p>
</form>
