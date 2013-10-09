<!DOCTYPE html>
<html>
<head>
    <title><%block name='title'>The Cave of Dragonflies ASB</%block></title>
    <link rel="stylesheet" href="/static/asb.css">
</head>
<body>
<section id="header">
<p style="text-align: center; margin: 0; padding: 2em;">banner goes here once I make it</p>

<div id="menu">
<ul id="menu-user">
% if False:  ## if logged in
  <li>Account stuff</li>
  <li>Buy stuff</li>
  <li>idk</li>
  <li>Log out</li>
% else:
  <li>Username [_____] Password [_____] [Log in]</li>
  <li><a href="/register">Register</a></li>
% endif
</ul>

<ul id="menu-dex">
  <li><a href="/trainers">Trainers</a></li>
  <li><a href="/pokemon">Pokémon</a></li>
  <li><a href="/pokemon/species">Species</a></li>
  <li>Items</li>
  <li>Moves?</li>
  <li>Abilities?</li>
</ul>
</div>
</section>

<section id="body">
${next.body()}\
</section>
</body>
</html>
