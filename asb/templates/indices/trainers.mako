<%inherit file='/base.mako'/>\
<%block name='title'>Trainers - The Cave of Dragonflies ASB</%block>\

<ul>
    % for t in trainers:
    <li><a href="/trainers/${t.identifier}">${t.name}</a></li>
    % endfor
</ul>
