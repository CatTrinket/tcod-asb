<%inherit file='/base.mako'/>\
<%block name='title'>Species list - Pokémon</%block>\

<ul>
    % for p in pokemon:
    <li><a href="/pokemon/species/${p.identifier}">#${p.number} ${p.name}</a></li>
    % endfor
</ul>
