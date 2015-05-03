<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%namespace name='sig' file='/sig_stuff/helpers.mako'/>\
<%block name='title'>Signature attributes awaiting approval - The Cave of Dragonflies ASB</%block>\

<h1>Signature attributes awaiting approval</h1>

% for sig_thing in form.sigs:
${sig.display_body_mod(sig_thing.sig, approval_form=sig_thing)}
% endfor