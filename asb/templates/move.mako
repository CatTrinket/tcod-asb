<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers.mako"/>\
<%block name='title'>${move.name} - Moves - The Cave of Dragonflies ASB</%block>\

<h1>${move.name}</h1>
<dl>
   <dt>Type</dt>
   <dd>${helpers.type_icon(move.type) | n}</dd>

   <dt>Base damage</dt>
   % if move.damage is None:
   <dd>—</dd>
   % elif move.damage == -1:
   <dd>Varies</dd>
   % else:
   <dd>${move.damage | n, str}%
   % endif

   <dt>Base energy</dt>
   % if move.energy is None:
   <dd>—</dd>
   % elif move.energy == -1:
   <dd>Varies</dd>
   % else:
   <dd>${move.energy | n, str}%</dd>
   % endif

   <dt>Accuracy</dt>
   % if move.accuracy is None:
   <dd>—</dd>
   % else:
   <dd>${move.accuracy | n, str}%</dd>
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
${helpers.pokemon_form_table(pokemon, squashed_forms=True)}
