<%inherit file='/base.mako'/>\
<%block name='title'>Trainers</%block>\

<ol>
    % for t in trainers:
    <li value="${str(t.id)}"><a href="/trainers/${str(t.id)}">${t.name}</a></li>
    % endfor
</ol>
