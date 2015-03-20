<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name="title">Reset password - The Cave of Dragonflies ASB</%block>

<h1>Request password reset</h1>
<p>Enter your username, and an email will be sent with a link to reset your
password.</p>

<form action="${request.path}" method="POST">
${form.csrf_token()}
${h.form_error_list(*form.errors.values())}

<p><b>${form.username.label}:</b> ${form.username} ${form.submit()}</p>
</form>
