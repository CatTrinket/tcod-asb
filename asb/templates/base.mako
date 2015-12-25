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
    <link rel="stylesheet" href="/static/icons.css">
    <link rel="icon" href="/static/images/favicon.png">
</head>

<%block name='body_tag'><body></%block>
<header>
<a href="/">
    <img src="/static/images/banner.png"
    alt="The Cave of Dragonflies ASB Database">
</a>

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
    <li><a href="/trade">Gifts</a></li>
    <li><a href="/settings">Settings</a></li>
  % else:
    <li><a href="/validate">Validate account</a></li>
  % endif

    <li><a href="/logout?csrf_token=${request.session.get_csrf_token()}">Log out</a></li>
% else:
    <li class="menu-focus-link"><a href="/register">Register</a></li>
    <li><a href="/reset-password">Reset password</a></li>
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
    <li><a href="/types">Types</a></li>
    <li><a href="/battles">Battles</a></li>
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

<footer>
<p>
<a href="http://forums.dragonflycave.com/forumdisplay.php?f=43">The Cave of
Dragonflies forums</a> •
<a href="http://github.com/Zhorken/tcod-asb">tcod-asb on GitHub</a>
</p>

<p>
TCoD ASBdb by <a href="http://github.com/Zhorken">Zhorken</a> •
Shiny Pokémon icon edits by
<a href="https://github.com/msikma/pokesprite">msikma</a><br>

Many thanks to
<a href="http://forums.dragonflycave.com/member.php?u=527">Negrek</a>,
<a href="http://forums.dragonflycave.com/member.php?u=190">Eifie</a>,
<a href="http://forums.dragonflycave.com/member.php?u=2243">Metallica Fanboy</a>,
<a href="http://forums.dragonflycave.com/member.php?u=2844">pathos</a>,
<a href="http://forums.dragonflycave.com/member.php?u=3374">The Omskivar</a>,
<a href="http://forums.dragonflycave.com/member.php?u=3541">Totodile</a>, and
<a href="http://forums.dragonflycave.com/member.php?u=95">ultraviolet</a>
</p>

<p>Pokémon © Nintendo, The Pokémon Company, GAME FREAK, Creatures Inc.</p>
</footer>
</body>
</html>
