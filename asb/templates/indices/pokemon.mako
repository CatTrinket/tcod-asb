<%inherit file='/base.mako'/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>Pokémon - The Cave of Dragonflies ASB</%block>\

% if show_all:
    <h1>All Pokémon</h1>
    <p>Showing all ${count} Pokémon in the league.</p>
    <p><a href="/pokemon">Show 100 newest Pokémon →</a></p>
% else:
    <h1>Newest Pokémon</h1>
    <p>Showing 100 most recently-obtained Pokémon in the league.</p>
    <p><a href="/pokemon?show-all=true">Show all ${count} Pokémon →</a></p>
% endif

${t.pokemon_table(pokemon)}
