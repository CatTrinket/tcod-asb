<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>${pokemon.name}'s sig stuff - Pokémon - The Cave of Dragonflies ASB</%block>\

<%def name="paragraphs(text)">
% if text is None:
None
% else:
% for line in text.splitlines():
% if line:
<p>${line}</p>
% endif
% endfor
% endif
</%def>

% if bodmod:
<h1>Body modification</h1>

<dl>
    <dt>Name</dt>
    <dd>${bodmod.name}

    <dt>Repeatable</dt>
    <dd>${bodmod.is_repeatable}</dd>

    <dt>Flavor</dt>
    <dd>
        ${paragraphs(bodmod.flavor)}
    </dd>

    <dt>Effect</dt>
    <dd>
        ${paragraphs(bodmod.effect)}
    </dd>
% endif

% if movemod:
<h1>Move modification</h1>

<dl>
    <dt>Name</dt>
    <dd>${movemod.name}

    <dt>Type</dt>
    <dd>${movemod.type}</dd>

    <dt>Power</dt>
    <dd>${movemod.power}</dd>

    <dt>Energy</dt>
    <dd>${movemod.energy}</dd>

    <dt>Accuracy</dt>
    <dd>${movemod.accuracy}</dd>

    <dt>Target</dt>
    <dd>${movemod.target}</dd>

    <dt>Gap</dt>
    <dd>${movemod.gap}</dd>

    <dt>Duration</dt>
    <dd>${movemod.duration}</dd>

    <dt>Stat</dt>
    <dd>${movemod.stat}</dd>

    <dt>Flavor</dt>
    <dd>
        ${paragraphs(movemod.flavor)}
    </dd>

    <dt>Effect</dt>
    <dd>
        ${paragraphs(movemod.effect)}
    </dd>
</dl>
% endif
