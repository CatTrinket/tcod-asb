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
% if mod.power is not None:
[b]Base Power[/b]: ${mod.power}
% elif mod.damage_class.identifier != 'non-damaging':
[b]Base Power[/b]: varies
% endif
% if mod.energy is not None:
[b]Energy[/b]: ${mod.energy}%
% else:
[b]Energy[/b]: varies
% endif
% if mod.accuracy is not None:
[b]Accuracy[/b]: ${mod.accuracy}
% else:
[b]Accuracy[/b]: —
% endif
[b]Target[/b]: ${mod.target.name}
% if mod.duration:
[b]Duration[/b]: ${mod.duration}
% endif

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

<%def name="display_move_mod(move, approval_form=None)">
<h2>
${move.name}
% if approval_form:
<form class="approval-form" action="approve-move" method="POST">
     ${approval_form.approve() | n} |
     <a href="${request.resource_url(move.pokemon) + 'move'}">Edit</a> |
     ${approval_form.deny() | n}
</form>
% endif
</h2>

<div class="sig-move-info">
% if approval_form:
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

% if not approval_form:
<dl>
    <dt>Duration</dt>
    % if move.duration:
    <dd>${move.duration}</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Usage Gap</dt>
    <dd>${move.gap}</dd>
</dl>
%endif
</div>

<dl>
    % if approval_form:
    <dt>Duration</dt>
    % if move.duration:
    <dd>${move.duration}</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Usage Gap</dt>
    <dd>${move.gap}</dd>
    %endif

    <dt>Description</dt>
    <dd>${move.description}</dd>

    <dt>Effects</dt>
    <dd>${move.effect}</dd>
</dl>
</%def>

<%def name="display_body_mod(mod, approval_form=None)">
<h2>
${mod.name}
% if approval_form:
<form class="approval-form" action="approve-attribute" method="POST">
     ${approval_form.approve() | n} |
     <a href="${request.resource_url(mod.pokemon) + 'attribute'}">Edit</a> |
     ${approval_form.deny() | n}
</form>
% endif
</h2>

<dl>
    % if approval_form:
    <dt>Pokémon</dt>
    <dd>${h.link(mod.pokemon)}</dd>

    <dt>Species</dt>
    <dd>${mod.pokemon.species.name}</dd>
    %endif

    <dt>Bio</dt>
    % if mod.description:
    <dd>${paragraphs(mod.description)}</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Effects</dt>
    <dd>${paragraphs(mod.effect)}</dd>
</dl>
</%def>
