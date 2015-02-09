<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>Post news - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md %>

<h1>Post news</h1>
<form id="news-form" action="/news/post" method="POST">
${form.csrf_token}
${h.form_error_list(*form.errors.values())}
<dl>
    <dt>${form.title.label}</dt>
    <dd>${form.title}</dd>

    <dt>${form.text.label}</dt>
    <dd>${form.text(rows=10, cols=100)}</dd>

    <dd>${form.preview} ${form.post}</dd>
</dl>

</form>

% if form.preview.data:
<h1>Preview</h1>
<h2>${form.title.data}</h2>
<p class="news-timestamp">
    Posted <b>${now.strftime('%Y %B %d, %H:%M.%S EST')}</b>
    by <b>${h.link(request.user)}</b>
</p>
${form.text.data | md.convert}
% endif
