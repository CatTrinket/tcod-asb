<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name="title">Reset password - The Cave of Dragonflies ASB</%block>

<h1>Reset password</h1>
<form action="${request.path}" method="POST">
${form.csrf_token()}
${h.form_error_list(*form.errors.values())}

<dl>
    <dt>${form.new_password.label}</dt>
    <dd>${form.new_password}</dd>

    <dt>${form.confirm_password.label}</dt>
    <dd>${form.confirm_password}</dd>
</dl>

${form.submit}
</form>
