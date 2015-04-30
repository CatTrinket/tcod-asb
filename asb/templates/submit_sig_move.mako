<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Submit Signature Move - The Cave of Dragonflies ASB</%block>\

<h1>${pokemon.name}'s Signature Move</h1>

<p>All trainers may use a Pokémon's movepool modification slot to teach it  an attack unique to that Pokémon and often more powerful or spectacular than the standard attacks that many different Pokémon can learn. Signature moves can be serious or silly, powerful or bizarre, complicated or straightforward, but keep in mind that all signature moves are subject to approval, and if your signature move proves to be unbalanced in battle, you may be asked to alter it.</p>

<form action="move" method="POST">
<%
    description_hint = "Give background as to how your Pokémon developed this move or how it came to have the ability to execute it. Explain how the attack is performed. It should be clear from the description why the attack has the effects that it does."

    effects_hint = "The effects of a signature move can include anything from stat boosts to causing your Pokémon to sprout wings. Everything besides damage that the attack accomplishes should go here, and if the damage and energy costs are not straightforward, or the attack can behave in variable ways, all its different permutations should be explained here. Only if the attack does absolutely nothing but cause damage should this field be left blank."
%>\
${form.csrf_token() | n}
${h.form_error_list(form.csrf_token.errors)}

<dl>
	<dt>${form.name.label() | n}</dt>
	<dd>${form.name(maxlength=50, size=50) | n}</dd>
    <dd>Your signature move's name should be different from that of any canon move.</dd>
	% for error in form.name.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.description.label() | n}</dt>
    <dd>${form.description(rows=10, cols=80, placeholder=description_hint) | n}</dd>
    % for error in form.description.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.move_type.label() | n}</dt>
    <dd>${form.move_type() | n}</dd>
    % for error in form.move_type.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.damage_class.label() | n}</dt>
    <dd>${form.damage_class() | n}</dd>
    % for error in form.damage_class.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.bp.label() | n}</dt>
    <dd>${form.bp() | n}</dd>
    <dd>The actual base power of the attack, <em>not</em> the base damage percentage. Leave blank if this attack doesn't do damage, or its damage varies.</dd>
    % for error in form.bp.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.energy.label() | n}</dt>
    <dd>${form.energy() | n}</dd>
    <dd>The energy percentage cost of the attack. Leave empty for variable.</dd>
    % for error in form.energy.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.accuracy.label() | n}</dt>
    <dd>${form.accuracy() | n}</dd>
    <dd>Leave blank if this attack cannot miss.</dd>
    % for error in form.accuracy.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.target.label() | n}</dt>
    <dd>${form.target() | n}</dd>
    % for error in form.target.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.duration.label() | n}</dt>
    <dd>${form.duration() | n}</dd>
    <dd>If the move's effects last for more than one action or it takes more than one action to perform, indicate here how long the attack and its effects last.</dd>
    % for error in form.duration.errors:
    <dd class="form-error">${error}</dd>
    % endfor

    <dt>${form.usage_gap.label() | n}</dt>
    <dd>${form.usage_gap() | n}</dd>
    <dd>How often can this move be used? If the attack has a duration, indicate whether its usage gap is from the time of use or the end of all effects.</dd>
    % for error in form.usage_gap.errors:
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