<%inherit file='/base.mako'/>\
<%block name="title">Login - The Cave of Dragonflies ASB</%block>

<form action="/login" method="POST" id="login-page-form">
    % if form.csrf_token.errors:
    <p class="form-error">
        Invalid CSRF token; the login form probably expired.  Try again.
    </p>
    % elif form.username.errors or form.password.errors:
    <p class="form-error">Invalid username or password.</p>
    % endif

    <!-- No ids on these fields because they don't need them for anything and
         they'd conflict with the login form in the menu -->
    ${form.csrf_token(id='') | n}
    <p>${form.username.label() | n} ${form.username(id='', maxlength=30) | n}</p>
    <p>${form.password.label() | n} ${form.password(id='') | n}</p>
    <p>${form.log_in(id='') | n}</p>
</form>
