#!XXPerlPathXX

# This is a CGI script to do a desc search of the oanda database.
# It is to be installed at XXDescSearchPathXX on XXServerNameXX.

# Set URL for this script.
$cgi_url = 'XXDescSearchUrlXX';

# Set title for form.
$form_title = 'Armory Description Search Form';

require 'XXCommonClientPathXX';

# Process arguments.
foreach $pair (split (/\&/, $ENV{'QUERY_STRING'})) {
  ($left, $right) = split (/[=]/, $pair, 2);
  $left = &decode ($left);
  $right = &decode ($right);

  $p = $right if ($left =~ 'p');
}

&print_header ();
if ($p ne '') {
  &connect_to_data_server ();

  print S 'd0 1 ', fixcase($p);
  print S 'EOF';

  $n = &get_matches ();
  
  $scoresort = 0;
  @matches = sort byblazon @matches;
}

print '<p>Enter an armory description code to search for.';
print '<a href="XXDescHintsPageUrlXX">Hints are available for this form.</a>';

print '<p>Armory Description: ';
print '<input type="text" name="p" value="', $p, '" size="40">';

print '<input type="submit" value="Search">';
print '</form>';

if ($p ne '') {
  print '<hr>';
  &print_results ("description=\"<i>".&escape($p)."</i>\"", $n, $scoresort);

  print '<a href="XXComplexSearchUrlXX?a=', $arm_descs, '&d=', $era, '&g=', $gloss_links, '&l=500&s=score+and+blazon&w1=1&m1=armory+description&p1=', &encode ($p), '">convert to complex search</a>'
}
&print_trailer ();
# end of XXDescSearchPathXX
