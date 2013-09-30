<%inherit file='/base.mako'/>\
<%block name='title'>Pokémon</%block>\

<ol>
    % for p in pokemon:
    <li value="${str(p.id)}"><a href="/pokemon/${p.identifier}"><strong>${p.name}</strong> the ${p.gender.name} ${p.species.name}</a>
    % endfor
</ol>
