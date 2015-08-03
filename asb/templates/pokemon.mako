<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
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
${h.pokemon_sprite(pokemon)}

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
