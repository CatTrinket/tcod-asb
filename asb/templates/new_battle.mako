<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>New battle - The Cave of Dragonflies ASB</%block>\

<h1>New battle</h1>

<form action="/battles/new" method="POST">
<p><label for="trainers">Enter battlers' names, one per line.  If this battle
is happening in teams, leave a blank line between teams.</label></p>

${h.form_error_list(*form.errors.values())}

${form.csrf_token}
${form.trainers(rows=10, cols=30)}
${form.submit}
</form>
