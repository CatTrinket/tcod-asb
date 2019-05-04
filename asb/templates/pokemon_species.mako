<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${pokemon.name} - Pokémon species - The Cave of Dragonflies ASB</%block>\

<%! from asb.markup.markdown import render as md %>

<h1>${pokemon.name}</h1>

<div class="portrait-block">
${h.pokemon_form_sprite(pokemon)}

% for type in pokemon.types:
${h.type_icon(type)}\
% endfor
</div>

<div class="beside-portrait">
<dl>
    <dt>Speed</dt>
    <dd>${pokemon.speed}</dd>

    % if pokemon.species.rarity is not None:
    <dt>Rarity</dt>
    <dd>
        ${pokemon.species.rarity_id}
        ($${pokemon.species.rarity.price})
    </dd>
    % endif

    <dt>Gender</dt>
    <dd>
        ${(
            ' or '.join(gender.name for gender in pokemon.species.genders)
            .capitalize()
        )}
    </dd>

    <dt>Population</dt>
    % if census:
    <dd><a href="#census">${len(census)}</a></dd>
    % else:
    <dd>0</dd>
    % endif
</dl>
</div>

<h2>Abilities</h2>

<dl class="ability-list">
    % for ability in abilities:
    % if ability.is_hidden:
    <dt class="hidden-ability">${h.link(ability.ability)}</dt>
    <dd>
        ${'_(Hidden ability.)_  {}'.format(ability.ability.summary) | md}
    </dd>
    % else:
    <dt>${h.link(ability.ability)}</dt>
    <dd>${ability.ability.summary | md}</dd>
    % endif
    % endfor
</dl>

<h2>Type matchups</h2>
<dl class="type-matchups">
    % for (label, types) in type_matchups.values():
    <dt>${label}</dt>
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

<h1 id="evolution">Evolution</h1>

<%def name="evo_method(method)">\
% if method is not None:
<% or_ = or_iter() %>
% if method.item_id is not None:
% if method.item.name.lower().startswith(('a', 'e', 'i', 'o', 'u')):
${next(or_) | n}battle holding an ${h.link(method.item)}\
% else:
${next(or_) | n}battle holding a ${h.link(method.item)}\
% endif
% endif
\
% if method.experience is not None:
${next(or_) | n}${method.experience} EXP\
% endif
\
% if method.happiness is not None:
${next(or_) | n}${method.happiness} happiness\
% endif
\
% if method.buyable_price is not None:
${next(or_) | n}pay $${method.buyable_price}\
% endif
\
% if method.gender_id is not None:
 (${method.gender.name} only)
% endif
% endif
</%def>

<table class="evolution-tree">
<thead>
    % for layer in evo_tree:
    <tr>
        % for evo, colspan in layer:
        <%
            current = evo == pokemon.species

            if (evo.identifier.endswith('-alola') or
                  evo.species.identifier == 'meowstic'):
                text = evo.name
            else:
                text = evo.species.name
        %>
        <td colspan="${colspan}" class="${'focus' if current else ''}">
            % if current:
            ${h.pokemon_form_icon(pokemon, alt='')}${evo.name}
            % else:
            ${h.pokemon_form_icon(evo, alt='')}${h.link(evo, text=text)}
            % endif

            % if evo.evolution_method is not None:
            <p class="evolution-method">${evo_method(evo.evolution_method)}</p>
            % endif
        </td>
        % endfor
    </tr>
    % endfor
</table>

% if len(pokemon.species.forms) > 1:
<h1>Forms</h1>

<ul id="species-form-list">
% for form in pokemon.species.forms:
% if form == pokemon:
<li class="focus portrait">
    <img src="/static/images/pokemon/${form.identifier}.png" alt="${form.name}">
</li>
% else:
<li class="portrait">
    <a href="${request.resource_path(form.__parent__, form.__name__)}">
        <img src="/static/images/pokemon/${form.identifier}.png" alt="${form.name}">
    </a>
</li>
% endif
% endfor
</ul>

% if pokemon.species.form_explanation:
    ${pokemon.species.form_explanation | md}
% endif
% endif

<h1>Moves</h1>
${t.move_table(pokemon.moves)}

% if census:
<h1 id="census">${pokemon.name} in the league</h1>
${t.pokemon_table(census, skip_cols=['species'])}
% endif
