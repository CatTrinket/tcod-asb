<%inherit file='/base.mako'/>\
<%block name='title'>Pokémon</%block>\

<ol>
    % for p in pokemon:
    <li value="${str(p.id)}"><a href="/pokemon/${str(p.id)}"><strong>${p.name}</strong> the ${p.gender.name} ${p.species.name}</a>
    % endfor
</ol>
