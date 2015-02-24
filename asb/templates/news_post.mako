<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>Post news - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md %>

<h1>Post news</h1>
<form id="news-form" action="${request.path}" method="POST">
${form.csrf_token}
${h.form_error_list(*form.errors.values())}
<dl>
    <dt>${form.title.label}</dt>
    <dd>${form.title}</dd>

    <dt>${form.text.label}</dt>
    <dd>${form.text(rows=10, cols=100)}</dd>

    <dd>${form.preview} ${form.post}</dd>
</dl>

% if delete_form is not undefined:
<h2>Delete</h2>
<!-- This form is deliberately within the same form element so that if someone
accidentally clicks delete (without the ticky), they won't lose their post -->
${delete_form.csrf_token}
${h.form_error_list(*delete_form.errors.values())}

<p>${delete_form.confirm.label.text} ${delete_form.confirm}</p>
${delete_form.delete}
% endif
</form>

% if post is not None:
<h1>Preview</h1>
${h.news_post(
    post,
    preview=True,
    title=form.title.data,
    text=form.text.data,
)}
% elif form.preview.data:
<h1>Preview</h1>
${h.news_post(
    preview=True,
    title=form.title.data,
    post_time=now,
    poster=request.user,
    text=form.text.data
)}
% endif
