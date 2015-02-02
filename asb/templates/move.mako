<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${move.name} - Moves - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md %>

% if request.has_permission('flavor.edit'):
<p><a href="${request.resource_path(move, 'edit')}">Edit ${move.name} →</a></p>
% endif

<h1>${move.name}</h1>

<div id="move-info">
<dl>
   <dt>Type</dt>
   <dd>${h.type_icon(move.type)}</dd>

   <dt>Stat</dt>
   <dd>${h.damage_class_icon(move.damage_class)}</dd>

   <dt>Target</dt>
   <dd>${move.target.name}</dd>

   <dt>Category</dt>
   <dd>${move.category or '???'}</dd>
</dl>

<dl>
   <dt>Base damage</dt>
   % if move.power is not None:
   <dd>${move.damage}% (${move.power} power)</dd>
   % elif move.damage_class.identifier == 'non-damaging':
   <dd>n/a</dd>
   ## XXX It'd be nice not to special-case these two
   % elif move.identifier == 'dragon-rage':
   <dd>4% (fixed)</dd>
   % elif move.identifier == 'sonic-boom':
   <dd>2% (fixed)</dd>
   % else:
   <dd>Varies</dd>
   % endif

   <dt>Base energy</dt>
   % if move.energy is None:
   <dd>—</dd>
   % elif move.energy == -1:
   <dd>Varies</dd>
   % else:
   <dd>${move.energy}%</dd>
   % endif

   <dt>Accuracy</dt>
   % if move.accuracy is None:
   <dd>—</dd>
   % else:
   <dd>${move.accuracy}%</dd>
   % endif

   <dt>Priority</dt>
   <dd>${h.num(move.priority, invisible_plus=False)}</dd>
</dl>

% if move.contest_category is not None:
<dl>
    <dt>Contest type</dt>
    <dd>${move.contest_category.name}

    % if move.appeal is not None:
    <dt>Appeal</dt>
    <dd>${h.appeal(move)}</dd>
    % endif

    % if move.jam is not None:
    <dt>Jam</dt>
    <dd>${h.jam(move)}</dd>
    % endif
</dl>
% endif
</div>

<h2>Summary</h2>
${move.effect.summary | md.convert, n}

<h1>Description</h1>
${move.effect.description | md.convert, n}

<h1>Pokémon</h1>
${t.pokemon_form_table(pokemon, squashed_forms=True)}
