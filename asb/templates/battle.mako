<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${battle.name} - Battles - The Cave of Dragonflies ASB</%block>\

<%def name="name(pokemon)">
<td class="icon pokemon-icon">${h.pokemon_form_icon(pokemon.form)}</td>
<td class="focus-column">\
% if pokemon.pokemon is not None:
${h.link(pokemon.pokemon, text=pokemon.name)}\
% else:
${pokemon.name}\
% endif
</%def>

% if request.has_permission('battle.e-ref'):
<p><a href="${request.resource_path(battle, 'e-ref')}">E-ref this battle →</a></p>
% endif

% if request.has_permission('battle.close'):
<p><a href="${request.resource_path(battle, 'close')}">Close this battle →</a></p>
% endif

% if request.has_permission('battle.approve'):
<p><a href="${request.resource_path(battle, 'approve')}">Approve this battle →</a></p>
% endif

% if request.has_permission('battle.edit'):
<p><a href="${request.resource_path(battle, 'edit')}">Edit this battle →</a></p>
% endif

% if request.has_permission('battle.link'):
<h1>BBCode</h1>
<p>Includes battlers' active squads and a link to this page.  You'll still have
to add the arena.</p>

<textarea readonly rows="15" cols="100">
[size=+2][b][u][url=${request.url}]${battle.name}[/url][/u][/b][/size]

% for team in battle.teams:
% if team.team_number > 1:


% endif
% if team_battle:
[b][u]Team ${team.team_number}[/u][/b]

% endif
% for n, trainer in enumerate(team.trainers):
% if n > 0:

% endif
[b]${trainer.name}'s active squad[/b]

% for pokemon in trainer.pokemon:
[sprite=party]\
% if pokemon.gender.identifier == 'female' and pokemon.species.identifier in \
    ['unfezant', 'frillish', 'jellicent', 'pyroar', 'meowstic']:
${pokemon.species.identifier}-f\
% elif pokemon.form.identifier == 'meowstic-male':
meowstic\
% else:
${pokemon.form.identifier}\
% endif
[/sprite] [b]${pokemon.name}[/b] the \
${pokemon.gender.name} ${pokemon.species.name} \
% if pokemon.species.form_carries_into_battle and \
    pokemon.form.form_name is not None:
(${pokemon.form.form_name}) \
% endif
<${pokemon.ability.name}>\
% if pokemon.item is not None:
 @ ${pokemon.item.name}\
% endif

% endfor
% endfor
% endfor
</textarea>

<p>Once you've created the thread, link it here:</p>

<form action="${request.path}" method="POST">
${link_form.csrf_token}
${link_form.link(size=60)} ${link_form.submit}
</form>

${h.form_error_list(*link_form.errors.values())}
% endif

<h1>${battle.name}</h1>
<dl>
    % if battle.tcodf_thread_id is not None:
    <dt>Thread link</dt>
    <dd><a href="${battle.link}">Thread #${battle.tcodf_thread_id}</a></dd>
    % endif

    <dt>Ref</dt>
    % if battle.ref is None:
    <dd>???</dd>
    % else:
    <dd>${h.link(battle.ref)}</dd>
    % endif

    % if battle.previous_refs:
    <dt>Previous refs</dt>
    <dd>
        % for ref in battle.previous_refs[:-1]:
        ${h.link(ref)},
        % endfor
        ${h.link(battle.previous_refs[-1])}
    </dd>
    % endif

    <dt>Started</dt>
    <dd>${battle.start_date.strftime('%Y %B %d')}</dd>

    % if battle.end_date is not None:
    <dt>Ended</dt>
    <dd>${battle.end_date.strftime('%Y %B %d')}</dd>

    %  if not battle.needs_approval:
    <dt>Winners</dt>
    <dd>${outcome}</dd>

    <dt>How did it end?</dt>
    <dd>${length}.</dd>
    % endif
    % endif
</dl>

% for team in battle.teams:
% if team_battle:
<h1>Team ${team.team_number}</h1>
% elif team.trainers[0].trainer is not None:
<h1>${h.link(team.trainers[0].trainer)}</h1>
% else:
<h1>${team.trainers[0].name}</h1>
% endif

${t.pokemon_table(
    *(trainer.pokemon for trainer in team.trainers),
    skip_cols=['name', 'trainer'],
    subheaders=(trainer.trainer for trainer in team.trainers)
        if team_battle else None,
    subheader_colspan=10,
    extra_left_cols=[{'col': t.name_col, 'th': t.name_header, 'td': name}],
    extra_right_cols=[{'col': t.ko_col, 'th': t.ko_header, 'td': t.ko_cell}]
        if battle.end_date is not None and not battle.needs_approval else [],
    highlight_condition=(lambda pokemon: pokemon.participated)
        if battle.end_date is not None and not battle.needs_approval else None,
    link_subheaders=True
)}
% endfor
