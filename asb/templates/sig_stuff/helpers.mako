<%namespace name="h" file="/helpers/helpers.mako"/>

<%def name="paragraphs(text)">
% if text is None:
None
% else:
% for line in text.splitlines():
% if line:
<p>${line}</p>
% endif
% endfor
% endif
</%def>

<%def name="display_pending_move_mod(pokemon)">\
<% mod = pokemon.move_modification %>\
<textarea readonly rows="10" cols="80">
[b]Pokémon[/b]: [url=${request.resource_url(pokemon)}]${pokemon.name}[/url] the ${pokemon.gender.name} ${pokemon.species.name}
[b]Ability[/b]: ${pokemon.ability.name}
[b]Signature Move[/b]: ${mod.name}

${mod.description}

[b]Type[/b]: ${mod.type.name}
[b]Damage Class[/b]: ${mod.damage_class.name}
[b]Base Power[/b]: ${mod.power}
[b]Energy[/b]: ${mod.energy}%
[b]Accuracy[/b]: ${mod.accuracy}
[b]Target[/b]: ${mod.target.name}
[b]Duration[/b]: ${mod.duration}

[b]Effects[/b]: ${mod.effect}

[b]Usage Gap[/b]: ${mod.gap}
</textarea>
</%def>

<%def name="display_pending_body_mod(pokemon)">\
<% mod = pokemon.body_modification %>\
<textarea readonly rows="10" cols="80">
[b]Pokémon[/b]: [url=${request.resource_url(pokemon)}]${pokemon.name}[/url] the ${pokemon.gender.name} ${pokemon.species.name}
[b]Ability[/b]: ${pokemon.ability.name}
[b]Signature Attribute[/b]: ${mod.name}

[b]Description[/b]: ${mod.description}

[b]Effects[/b]: ${mod.effect}
</textarea>
</%def>

<%def name="display_move_mod(move, show_approval=False)">
<h2>
${move.name}
% if show_approval:
<span class="approval-links">
     <a href="#">Approve</a> |
     <a href="${request.resource_url(move.pokemon) + 'move'}">Edit</a> |
     <a href="#">Deny</a>
</span>
% endif
</h2>

<div class="sig-move-info">
% if show_approval:
<dl>
    <dt>Pokémon</dt>
    <dd>${h.link(move.pokemon)}</dd>

    <dt>Species</dt>
    <dd>${move.pokemon.species.name}</dd>
</dl>

%endif
<dl>
   <dt>Type</dt>
   <dd>${h.type_icon(move.type)}</dd>

   <dt>Stat</dt>
   <dd>${h.damage_class_icon(move.damage_class)}</dd>

   <dt>Target</dt>
   <dd>${move.target.name}</dd>
</dl>

<dl>
   <dt>Base power</dt>
   % if move.power is not None:
   <dd>${move.power}</dd>
   % elif move.damage_class.identifier == 'non-damaging':
   <dd>n/a</dd>
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
</dl>
</div>

<dl>
    <dt>Description</dt>
    <dd>${move.description}</dd>

    <dt>Effects</dt>
    <dd>${move.effect}</dd>
</dl>
</%def>

<%def name="display_body_mod(mod, show_approval=False)">
<h2>
${mod.name}
% if show_approval:
<span class="approval-links">
     <a href="#">Approve</a> |
     <a href="${request.resource_url(mod.pokemon) + 'attribute'}">Edit</a> |
     <a href="#">Deny</a>
</span>
% endif
</h2>

<dl>
    % if show_pokemon:
    <dt>Pokémon</dt>
    <dd>${h.link(mod.pokemon)}</dd>

    <dt>Species</dt>
    <dd>${mod.pokemon.species.name}</dd>
    %endif

    <dt>Bio</dt>
    <dd>${paragraphs(mod.description)}</dd>

    <dt>Effects</dt>
    <dd>${paragraphs(mod.effect)}</dd>
</dl>
</%def>
