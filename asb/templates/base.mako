<%
    from asb.views.user import LoginForm
    login_form = LoginForm(csrf_context=request.session)
%>\
\
<!DOCTYPE html>
<html>
<head>
    <title><%block name='title'>The Cave of Dragonflies ASB</%block></title>
    <link rel="stylesheet" href="/static/asb.css">
</head>
<body>
<header>
<a href="/"><img src="/static/images/banner.png"></a>

<nav>
<ul id="menu-user">
% if request.user is not None:
    <li class="menu-focus-link"><a href="/trainers/${request.user.identifier}">${request.user.name}</a></li>

  % if request.user.is_validated:
    % if request.user.has_pokemon:
    <li><a href="/pokemon/manage">Your Pokémon</a></li>
    % else:
    <li><a href="/pokemon/buy">Buy Pokémon</a></li>
    % endif

    % if request.user.has_items:
    <li><a href="/items/manage">Your items</a></li>
    % else:
    <li><a href="/items/buy">Buy items</a></li>
    % endif

    <li><a href="/bank">Bank</a></li>
    <li><a href="/settings">Settings</a></li>
  % else:
    <li><a href="/validate">Validate account</a></li>
  % endif

    <li><a href="/logout?csrf_token=${request.session.get_csrf_token()}">Log out</a></li>
% else:
    <li class="menu-focus-link"><a href="/register">Register</a></li>
    <li>
      <form action="/login" method="POST" id="login">
        ${login_form.csrf_token(id='login-csrf') | n}
        ${login_form.username.label() | n} ${login_form.username(maxlength=30) | n}
        ${login_form.password.label() | n} ${login_form.password() | n}
        ${login_form.log_in() | n}
      </form>
    </li>
% endif
</ul>

<ul id="menu-dex">
    <li><a href="/trainers">Trainers</a></li>
    <li><a href="/pokemon">Pokémon</a></li>
    <li><a href="/species">Species</a></li>
    <li><a href="/moves">Moves</a></li>
    <li><a href="/abilities">Abilities</a></li>
    <li><a href="/items">Items</a></li>
</ul>
</nav>

<% flash = request.session.pop_flash() %>
% if flash:
<div id="flash">
<ul>
    % for message in flash:
    <li>${message}</li>
    % endfor
</ul>
</div>
% endif
</header>

<main>
${next.body()}\
</main>
</body>
</html>
