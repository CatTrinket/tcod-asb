<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>Evolve ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>

<%block name='body_tag'>
% if pokemon.species.identifier == 'inkay':
<body class="topsy-turvy">
% else:
<body>
% endif
</%block>

<h1>What?  ${pokemon.name} is evolving!</h1>

<form id="evolution-form" action="evolve" method="POST">
    % if form.errors:
    <ul class="form-error">
        % for field, errors in form.errors.items():
        % for error in errors:
        <li>${error}</li>
        % endfor
        % endfor
    </ul>
    % endif

    ${form.csrf_token() | n}

    <ul>
        % for (evo, buy, item), option in zip(evolutions, form.evolution):
        <li>
            <label>
            ${h.pokemon_form_sprite(evo, gender=pokemon.gender.identifier)}

            <p class="evolution-name">${evo.species.name}</p>

            % if evo.form_name:
            <p class="evolution-note">${evo.form_name}</p>
            % endif

            % if buy:
            <p class="evolution-note">
                (Costs $${evo.evolution_method.buyable_price})
            </p>
            % endif

            % if item:
            <p class="evolution-note">
                (Uses up a held ${evo.evolution_method.item.name})
            </p>
            % endif

            ${option() | n}
            </label>
        </li>
        % endfor
    </ul>
    ${form.submit() | n}
</form>
