<%inherit file='/base.mako'/>
<%namespace name="helpers" file="/helpers/helpers.mako"/>
<%namespace name="markup" file="/helpers/markup.mako"/>

<%block name='title'>
    Edit profile - Trainers - The Cave of Dragonflies ASB
</%block>


% if trainer == request.user:
    <h1>Edit your profile</h1>
% else:
    <h1>Edit ${trainer.name}'s profile</h1>
% endif

<form action="${request.path}" method="POST" class="editor">
    ${form.csrf_token()}
    ${helpers.form_error_list(form.csrf_token.errors)}

    ${markup.markup_editor(form.profile, form.profile_format)}

    <p>${form.preview} ${form.save}</p>
</form>

% if form.preview.data:
    <h2>Preview</h2>
    ${markup.markup(form.profile.data, form.profile_format.data)}
% endif
