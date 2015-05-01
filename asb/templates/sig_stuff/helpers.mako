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

<%def name="display_move_mod(mod)">
<dl>
    <dt>Name</dt>
    <dd>${mod.name}</dd>

    <dt>Type</dt>
    <dd>${mod.type.name}</dd>

    <dt>Base Power</dt>
    % if mod.power:
    <dd>${mod.power}</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Energy</dt>
    % if mod.energy:
    <dd>${mod.energy}%</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Accuracy</dt>
    % if mod.accuracy:
    <dd>${mod.accuracy}</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Target</dt>
    <dd>${mod.target.name}</dd>

    <dt>Damage Class</dt>
    <dd>${mod.damage_class.name.capitalize()}</dd>

    <dt>Duration</dt>
    % if mod.duration:
    <dd>${mod.duration}</dd>
    % else:
    <dd>—</dd>
    % endif

    <dt>Usage Gap</dt>
    <dd>${mod.gap}</dd>

    <dt>Description</dt>
    <dd>${paragraphs(mod.description)}</dd>

    <dt>Effects</dt>
    <dd>${paragraphs(mod.effect)}</dd>
</dl>
</%def>

<%def name="display_body_mod(mod)">
<dl>
    <dt>Name</dt>
    <dd>${mod.name}</dd>

    <dt>Bio</dt>
    <dd>${paragraphs(mod.description)}</dd>

    <dt>Effects</dt>
    <dd>${paragraphs(mod.effect)}</dd>
</dl>
</%def>
