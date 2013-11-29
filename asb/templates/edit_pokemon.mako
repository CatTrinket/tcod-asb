<%inherit file='/base.mako'/>\
<%block name='title'>Edit ${pokemon.name} - Pokémon - The Cave of Dragonflies ASB</%block>\

<h1>Edit ${pokemon.name}</h1>

<form action="edit" method="POST">
    ${form.csrf_token() | n}
    <p>
        ${form.name.label() | n} ${form.name() | n}
        ${form.save() | n}
    </p>
</form>
