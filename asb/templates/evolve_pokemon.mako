<%inherit file='/base.mako'/>\
<%block name='title'>Evolve ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Evolve ${pokemon.name}</h1>

<form action="evolve" method="POST">
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
    ${form.evolution() | n}
    ${form.submit() | n}
</form>
