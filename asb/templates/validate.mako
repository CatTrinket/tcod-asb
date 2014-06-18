<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name="title">Register - The Cave of Dragonflies ASB</%block>

<h1>Validate account</h1>

<p>In order to buy Pokémon (or get your old Pokémon back, if applicable),
you'll have to link your ASB and forum profiles back and forth.</p>

<hr>

<p>First, paste this link to your ASB profile into the "ASB profile" field on
your forum profile (User CP → Edit Your Details → ASB profile link):</p>

<p><code>
    ${request.resource_url(request.user.__parent__, request.user.__name__)}
</code></p>

<hr>

<p>Once you've done that, paste a link to your forum profile into the field
below:</p>

<form action="/validate" method="POST">
    ${form.csrf_token() | n}
    ${h.form_error_list(form.csrf_token.errors)}

    ${form.profile_link(size=50) | n}
    ${h.form_error_list(form.profile_link.errors)}

    ${form.submit() | n}
</form>
