<%inherit file='/base.mako'/>\
<%block name="title">Register - The Cave of Dragonflies ASB</%block>
<form action="/register" method="POST" id="registration-form">
    ${form.what_do.label() | n}
    ${form.what_do() | n}


    <hr>


    ${form.username.label() | n}
    ${form.username() | n}

    % if form.username.errors:
    <ul>
        % for error in form.username.errors:
        <li>${error}</li>
        % endfor
    </ul>
    % endif

    <p>If you're recovering an old profile, you'll have to enter your username
    as it was on October 4, 2013.  If you can't remember, find one of your
    posts on the forums and hover over your username to get a list of previous
    usernames.</p>


    <hr>


    ${form.password.label() | n}
    ${form.password() | n}

    ${form.password_confirm.label() | n}
    ${form.password_confirm() | n}

    <% pw_errors = form.password.errors + form.password_confirm.errors %>
    % if pw_errors:
    <ul>
        % for error in pw_errors:
        <li>${error}</li>
        % endfor
    </ul>
    % endif

    <p>This is separate from your forum password, but you can make it the same
    if you want.  Nobody can see it either way.</p>


    <hr>


    ${form.email.label() | n}
    ${form.email() | n}

    <p>Eventually this will be used to reset your password if you forget it.
    Until then (or if you never set an email) you'll have to wait for an ASB
    mod to take care of it manually.</p>


    <p>${form.submit() | n}</p>
</form>
