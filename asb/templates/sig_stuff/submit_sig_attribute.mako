<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Submit Signature Attribute - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}'s Signature Attribute</h1>

<p>A signature attribute is something about a Pokémon's physical capabilities or appearance that make it notably different than others of its species. It's free to apply for and add a signature attribute to your Pokémon, but all signature attributes are subject to approval, and if your signature attribute proves to be unbalanced in battle, you may be asked to alter it.</p>

<form action="${action}" method="POST">
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<dl>
	<dt>${form.name.label() | n}</dt>
	<dd>${form.name(maxlength=50, size=50) | n}</dd>
	% for error in form.name.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <%
	bio_hint = "Describe why and how your Pokémon is different from others of its species and how it came to be that way. This section has no bearing on approval, but it is where you can expand on your Pokémon's backstory and explain how it yields the effects you want your attribute to have."

	effects_hint = "Actually describe the specific effects of your signature attribute concretely and in game terms. For example, if your Umbreon secretes especially poisonous sweat during battle that has a \"slight chance\" of poisoning the foe upon contact, what is that chance, exactly? Five percent? Ten?\n\nRemember that if you want any really significant effects, you're going to need to pay for them by giving your attribute a drawback as well."
	%>\
    <dt>${form.bio.label() | n}</dt>
    <dd>${form.bio(rows=10, cols=80, placeholder=bio_hint) | n}</dd>
    % for error in form.bio.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.effects.label() | n}</dt>
    <dd>${form.effects(rows=10, cols=80, placeholder=effects_hint) | n}</dd>
    % for error in form.effects.errors:
    <dd class="form-error">${error}</dd>
    % endfor
</dl>

${form.submit() | n}
</form>