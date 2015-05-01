<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="sig" file="sig_stuff.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

% if request.has_permission('edit.basics', pokemon):
<p><a href="${request.resource_url(pokemon, 'edit')}">
    Edit ${pokemon.name} →
</a></p>
% endif

% if request.has_permission('edit.everything', pokemon):
<p><a href="${request.resource_url(pokemon, 'super-edit')}">
    Super-edit ${pokemon.name} →</a>
</p>
% endif

% if can_evolve and request.has_permission('edit.evolve', pokemon):
<p><a href="${request.resource_url(pokemon, 'evolve')}">
    Evolve ${pokemon.name} →
</a></p>
% endif

<h1>${pokemon.name}</h1>
<div class="portrait-block">
${h.pokemon_form_sprite(pokemon.form, gender=pokemon.gender.identifier)}

${h.link(pokemon.form, text=pokemon.species.name)}
% if (pokemon.gender.identifier != 'genderless' and \
    pokemon.species.identifier not in ['nidoran-f', 'nidoran-m']):
${h.gender_symbol(pokemon.gender)}
% endif
</div>

<div class="beside-portrait">
<dl>
    <dt>Trainer</dt>
    <dd>${h.link(pokemon.trainer)}</dd>

    <dt>Ability</dt>
    <dd>
        % if pokemon.ability_slot == 3:
            <span class="hidden-ability">
        % endif
        ${h.link(pokemon.ability)}
        % if pokemon.ability_slot == 3:
            </span>
        % endif
    </dd>

    <dt>Item</dt>
    <dd>
        % if pokemon.item is not None:
            ${h.link(pokemon.item)}
        % else:
            None
        %endif
    </dd>

    <dt>Experience</dt>
    <dd>
        ${pokemon.experience}
        % if 'experience' in evo_info:
        <span class="evolution-progress">${h.link(
            pokemon.form,
            text='/ {0}'.format(evo_info['experience']),
            anchor='evolution'
        )}</span>
        % endif
    </dd>

    <dt>Happiness</dt>
    <dd>
        ${pokemon.happiness}
        % if 'happiness' in evo_info:
        <span class="evolution-progress">${h.link(
            pokemon.form,
            text='/ {0}'.format(evo_info['happiness']),
            anchor='evolution'
        )}</span>
        % endif
    </dd>
</dl>
</div>

% if pokemon.move_modification or pokemon.body_modification or request.has_permission('edit.basics', pokemon):
<h1>Modifications</h1>

<h2><a name="move-mod">Move Modification</a></h2>

% if pokemon.move_modification:
% if pokemon.move_modification.needs_approval:
% if request.has_permission('edit.basics', pokemon):
<p>${pokemon.name}'s move modification is still pending approval. If you haven't already, paste the following into the [something] thread to let the approvers review it.</p>

${sig.display_pending_move_mod(pokemon)}
% endif
% else:
${sig.display_move_mod(pokemon.move_modification)}
% endif
% elif request.has_permission('edit.basics', pokemon):
<p><a href="${request.resource_url(pokemon, 'move')}">
    Give ${pokemon.name} a signature move →
</a></p>
% endif

<h2><a name="body-mod">Body Modification</a></h2>
% if pokemon.body_modification:
% if pokemon.body_modification.needs_approval:
% if request.has_permission('edit.basics', pokemon):
<p>${pokemon.name}'s body modification is still pending approval. If you haven't already, paste the following into the [something] thread to let the approvers review it.</p>

${sig.display_pending_body_mod(pokemon)}
% endif
% else:
${sig.display_body_mod(pokemon.body_modification)}
% endif
% elif request.has_permission('edit.basics', pokemon):
<p><a href="${request.resource_url(pokemon, 'attribute')}">
    Give ${pokemon.name} a signature attribute →
</a></p>
% endif
% endif
