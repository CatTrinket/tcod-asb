<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name="title">Register - The Cave of Dragonflies ASB</%block>
<form action="/register" method="POST" id="registration-form">
    ${form.csrf_token() | n}
    ${h.form_error_list(form.csrf_token.errors)}


    ${form.username.label() | n}
    ${form.username(maxlength=30) | n}
    ${h.form_error_list(form.username.errors)}


    <hr>


    ${form.password.label() | n}
    ${form.password() | n}

    ${form.password_confirm.label() | n}
    ${form.password_confirm() | n}

    ${h.form_error_list(form.password.errors, form.password_confirm.errors)}

    <p>This is separate from your forum password, but you can make it the same
    if you want.  Nobody can see it either way.</p>


    <hr>


    ${form.email.label() | n}
    ${form.email() | n}

    <p>Eventually this will be used to reset your password if you forget it.
    Until then you'll have to get Zhorken to take care of it manually.</p>


    <p>${form.submit() | n}</p>
</form>
