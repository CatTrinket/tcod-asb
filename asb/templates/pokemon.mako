<%inherit file='/base.mako'/>\
<%namespace name="helpers" file="/helpers/helpers.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

% if request.has_permission('edit.basics', pokemon):
<p><a href="${request.resource_url(pokemon, 'edit')}">Edit ${pokemon.name} →</a></p>
% endif
% if can_evolve and request.has_permission('edit.evolve', pokemon):
<p><a href="${request.resource_url(pokemon, 'evolve')}">Evolve ${pokemon.name} →</a></p>
% endif

<h1>${pokemon.name}</h1>

<dl>
    <dt>Name</dt>
    <dd>${pokemon.name}</dd>

    <dt>Species</dt>
    <dd>
        ${helpers.link(pokemon.form)}${helpers.pokemon_form_icon(pokemon.form,
                                       gender=pokemon.gender.identifier)}
    </dd>

    <dt>Trainer</dt>
    <dd>${helpers.link(pokemon.trainer)}</dd>

    <dt>Item</dt>
    <dd>
        % if pokemon.item is not None:
            ${helpers.link(pokemon.item)}
        % else:
            None
        %endif
    </dd>
</dl>

<h2>Stats</h2>

<%
    needed_experience = None
    needed_happiness = None

    evolution_methods = [evolution.evolution_method for evolution
        in pokemon.species.evolutions]
    for method in evolution_methods:
        if method.experience is not None:
            needed_experience =  method.experience
        if method.happiness is not None:
            needed_happiness = 4
%>

<dl>
    <dt>Gender</dt>
    <dd>${pokemon.gender.name.capitalize()}</dd>

    <dt>Ability</dt>
    <dd>
        % if pokemon.ability_slot == 3:
            <span class="hidden-ability">
        % endif
        ${helpers.link(pokemon.ability)}
        % if pokemon.ability_slot == 3:
            </span>
        % endif
    </dd>

    <dt>Experience</dt>
    <dd>
        ${pokemon.experience}
        % if needed_experience is not None:
            / ${needed_experience}
        % endif
    </dd>

    <dt>Happiness</dt>
    <dd>
        ${pokemon.happiness}
        % if needed_happiness is not None:
            / ${needed_happiness}
        % endif
    </dd>
</dl>

<h1>Signature Attributes</h1>
