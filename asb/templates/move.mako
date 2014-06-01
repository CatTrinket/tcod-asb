<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${move.name} - Moves - The Cave of Dragonflies ASB</%block>\

<h1>${move.name}</h1>
<dl>
   <dt>Type</dt>
   <dd>${h.type_icon(move.type) | n}</dd>

   <dt>Base damage</dt>
   % if move.damage is None:
   <dd>—</dd>
   % elif move.damage == -1:
   <dd>Varies</dd>
   % else:
   <dd>${move.damage}%
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

   <dt>Damage class</dt>
   <dd>${move.damage_class.name.capitalize()}</dd>

   <dt>Target</dt>
   <dd>${move.target or '???'}</dd>

   <dt>Category</dt>
   <dd>${move.category or '???'}</dd>
</dl>

<h2>Summary</h2>
<p>${move.summary}</p>

<h1>Effect</h1>
<p>${move.description}</p>

<h1>Pokémon</h1>
${t.pokemon_form_table(pokemon, squashed_forms=True)}
