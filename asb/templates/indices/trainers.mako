<%inherit file='/base.mako'/>\
<%block name='title'>Trainers</%block>\

<ul>
    % for t in trainers:
    <li><a href="/trainers/${t.identifier}">${t.name}</a></li>
    % endfor
</ul>
