<%inherit file='/base.mako'/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${item.name} - Items - The Cave of Dragonflies ASB</%block>\
<% from asb.markdown import md, chomp %>

% if request.has_permission('flavor.edit'):
<p><a href="${request.resource_path(item, 'edit')}">Edit ${item.name} →</a></p>
% endif

<h1>${item.name}</h1>
<dl>
    <dt>Category</dt>
    <dd>${item.category.name}</dd>

    <dt>Price</dt>
    % if item.price is not None:
    <dd>$${item.price}</dd>
    % else:
    <dd>Unbuyable</dd>
    % endif

    <dt>Summary</dt>
    <dd>${item.summary | md.convert, chomp}</dd>
</dl>


<h1>Description</h1>
${item.description | md.convert}

% if move_category is not None:
<h2>${move_category.name} moves</h2>
${t.move_table(move_category.moves)}
% endif
