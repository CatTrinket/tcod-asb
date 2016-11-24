<%inherit file='/base.mako'/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${ability.name} - Abilities - The Cave of Dragonflies ASB</%block>\
<% from asb.markdown import md %>

% if request.has_permission('flavor.edit'):
<p><a href="${request.resource_path(ability, 'edit')}">Edit ${ability.name} →</a></p>
% endif

<h1>${ability.name}</h1>
${'**Summary:** {0}'.format(ability.summary) | md.convert, n}

<h1>Description</h1>
${ability.description | md.convert, n}

% if ability.notes:
<h2>Notes</h2>
${ability.notes | md.convert, n}
% endif

% if move_category is not None:
<h2>${move_category.name} moves</h2>
${t.move_table(move_category.moves)}
% endif

<h1>Pokémon</h1>
${t.pokemon_form_table(normal_pokemon, hidden_pokemon,
    subheaders=('Regular ability', 'Hidden ability'), squashed_forms=True)}
