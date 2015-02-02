<%inherit file='/base.mako'/>\
<%block name='title'>Edit ${thing.name} - The Cave of Dragonflies ASB</%block>\
<% from asb.markdown import md %>

<h1>Edit ${thing.name}</h1>
<form action="${request.path}" method="POST" class="flavor-editor">
${form.csrf_token}

<dl>
    <dt>${form.summary.label}</dt>
    <dd>${form.summary}</dd>

    <dt>${form.description.label}</dt>
    <dd>${form.description(rows=10, cols=100)}</dd>
</dl>

${form.preview}
${form.save}
</form>

<h1>Preview</h1>
${'**Summary:** ' + form.summary.data | md.convert, n}
<hr>
${form.description.data | md.convert, n}
