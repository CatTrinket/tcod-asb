<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${move.name} - Moves - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md, chomp %>

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
   % if move.energy == 0:
   <dd>—</dd>
   % elif move.energy is None:
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

<dl>
    % for category in move.categories:
    <dt>${category.name}</dt>
    <dd>${category.description | md.convert, chomp}</dd>
    % endfor
</dl>
</div>

% if matchups is not None:
<h2>Type matchups</h2>
<dl class="type-matchups">
    % for (result, types) in matchups.items():
    <dt>${matchup_labels[result]}</dt>
    <dd>
        % if types:
        % for type in types:
${h.type_icon(type)}\
        % endfor
        % else:
        None
        % endif
    </dd>
    % endfor
</dl>
% endif

<h2>Summary</h2>
${move.effect.summary | md.convert, n}

<h1>Description</h1>
${move.effect.description | md.convert, n}

<h1>Pokémon</h1>
${t.pokemon_form_table(pokemon, squashed_forms=True)}
