<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers.mako'/>\
<%block name='title'>Evolve ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

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
            ${h.pokemon_form_sprite(evo, gender=pokemon.gender.identifier)}
            ${option.label() | n}
            <p class="evolution-note">
                % if buy:
                (Costs $${evo.species.evolution_method.buyable_price | n, str})
                % elif item:
                (Uses up a held ${evo.species.evolution_method.item.name})
                % else:
                &nbsp;
                % endif
            </p>
            ${option() | n}
        </li>
        % endfor
    </ul>
    ${form.submit() | n}
</form>
