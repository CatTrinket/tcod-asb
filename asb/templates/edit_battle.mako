<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Edit ${battle.name} - Battles - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${battle.name}</h1>
<h2>Refs</h2>
<form action="${request.path}" method="POST">
${form.csrf_token()}
${h.form_error_list(form.csrf_token.errors)}

<table>
<thead>
    <tr>
        <th>Name</th>
        <th><abbr title="Current">C</th>
        <th><abbr title="Emergency">E</th>
    </tr>
</thead>
<tbody>
    % for row in form.refs:
    <tr>
        <td>${row.ref}</td>
        <td>${row.current}</td>
        <td>${row.emergency}</td>
    </tr>

    % for errors in row.errors.values():
    % for error in errors:
    <tr class="form-error">
        <td colspan="3">${error}</td>
    </tr>
    % endfor
    % endfor
    % endfor
</tbody>
</table>

${form.save}
</form>
