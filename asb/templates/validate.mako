<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name="title">Register - The Cave of Dragonflies ASB</%block>

<h1>Validate account</h1>

<p>In order to buy Pokémon (or get your old Pokémon back, if applicable),
you'll have to link your ASB and forum profiles back and forth.</p>

<hr>

<p>First, paste this link into the "ASB profile link" field on your forum
profile (<a href="https://forums.dragonflycave.com/account/account-details">\
Account details</a> → ASB profile link):</p>

<p><code>
    ${request.resource_url(request.user.__parent__, request.user.__name__)}
</code></p>

<hr>

<p>Once you've done that, paste a link to your forum profile into the field
below:</p>

<form action="/validate" method="POST">
    ${form.csrf_token() | n}

    ${form.profile_link(size=50) | n}
    ${h.form_error_list(*form.errors.values())}

    ${form.submit() | n}
</form>
