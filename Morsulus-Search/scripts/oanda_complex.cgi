#!XXPerlPathXX

# This is a CGI script to do a complex search of the oanda database.
# It is to be installed at XXComplexSearchPathXX on XXServerNameXX.

# Set URL for this script.
$cgi_url = 'XXComplexSearchUrlXX';

require 'XXCommonClientPathXX';

# Set title for form.
$form_title = 'Complex Search Form';

$criteria = 10;

# option settings

@methods = ('', 'armory description', 'name pattern', 'record type', 'blazon pattern', 'broad name');

sub capitalize_words {
  local $_ = shift;
  s/\b(\w)/uc($1)/eg;
  "$_";
}
%methods = map { $_ => capitalize_words($_) } @methods;

@sorts = ('name only', 'last action date', 'blazon');
$sort = 'blazon';  # default

foreach $pair (split (/\&/, $ENV{'QUERY_STRING'})) {
  ($left, $right) = split (/=/, $pair, 2);
  $left = &decode ($left);
  $right = &decode ($right);

  if ($left =~ /^w(\d+)$/) { 
    $weight[$1] = $right if ($1 > 0 && $1 <= $criteria);
  } elsif ($left =~ /^m(\d+)$/) {
    $method[$1] = $right if ($1 > 0 && $1 <= $criteria);
  } elsif ($left =~ /^p(\d+)$/) {
    $p[$1] = $right if ($1 > 0 && $1 <= $criteria);
  }
  $arm_descs = $right if ($left eq 'a');
  $era = $right if ($left eq 'd');
  $gloss_links = $right if ($left eq 'g');
  $limit = $right if ($left eq 'l');
  $minimum_score = $right if ($left eq 'm');
  $scoresort = $right if ($left eq 'r');
  $sort = $right if ($left eq 's');
}
$limit = 500
  if ($limit !~ /^\d+$/);
$scoresort = 1 if ( ! defined $minimum_score );
$minimum_score = 1 if ( $minimum_score !~ /^[-]?\d+$/);

&print_header ();
print "<p>Criteria with no pattern are ignored. The weight and method are preloaded to make life simpler for mobile users.\n";

$invalid = 0;
$valid = 0;
$maximum_score = 0;
for $i (1 .. $criteria) {
    next if $p[$i] eq '';
  if ($weight[$i] !~ /^[+&-]?\d+$/) {
    if ($method[$i] ne '') {
      print "<h4>You specified an invalid weight ($weight[$i]) for criterion #$i; a weight must be an integer.</h4>";
      $invalid++;
    }
  } else {
    if ($method[$i] eq '') {
      print "<h4>You specified a weight ($weight[$i]) for criterion #$i without specifying a search method.</h4>";
      $invalid++;
    } else {
      $valid++;
      $maximum_score += $weight[$i];
    }
  }
}

my $cutoff_score = ( $minimum_score < 1 ) ? $maximum_score + $minimum_score : $minimum_score;
$cutoff_score = 1 if ( ! $cutoff_score or $cutoff_score !~ /^\d+$/ );

if ($valid > 0 && $invalid == 0) {
  &connect_to_data_server ();

  print S 'l ', $limit;
  
  for $i (1 .. $criteria) {
    next if $p[$i] eq '';
    if ($method[$i] eq 'name pattern') {
      print S "e1 $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'record type') {
      $temp = $p[$i];
      s/([^\\])?/$1\\?/g;
      print S "e3 $weight[$i] ^($p[$i])\$";
    } elsif ($method[$i] eq 'armory description') {
        $p[$i] = fixcase($p[$i]);
      print S "d0 $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'blazon pattern') {
      print S "ebi $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'broad name') {
      print S "n $weight[$i] $p[$i]";
    }
  }
  print S 't 0 ', $cutoff_score if ( $cutoff_score != 1 );
  print S 'EOF';

  $n = &get_matches ();
  
  if ($sort eq 'blazon') {
    if ( $scoresort ) {
      @matches = sort byscoreblazon @matches;
    } else {
      @matches = sort byblazon @matches;
    }
  } elsif ($sort eq 'last action date') {
    if ( $scoresort ) {
      @matches = sort byscoredate @matches;
    } else {
      @matches = sort bylastdate @matches;
    }
  } else {
    if ( $scoresort ) {
      @matches = sort byscorename @matches;
    } else {
      @matches = sort byname @matches;
    }
  }
}
  
print '<p>There are <a href="XXSearchMenuUrlXX">other search forms</a> available.';
print 'For help using this form, please refer to the <a href="XXComplexHintsPageUrlXX">hints page</a>.';
  
print '<h3>Scoring criteria:</h3><ol>';
for $i (1 .. $criteria) {
  $weight[$i] = 1 if $weight[$i] eq undef;
  $method[$i] = 'armory description' unless $method[$i];
  print '<li>weight=';
  print '<input type="text" name="w', $i, '" value="', $weight[$i], '" size=3>';

  # method selector
  print 'method=';
  &select ("m$i", $method[$i], @methods, \%methods);

  print 'pattern=';
  print '<input type="text" name="p', $i, '" value="', $p[$i], '" size=60>';
}
print '</ol>';

&display_options (1);

print '<h3>Actions:</h3>';
print '<input type="submit" value="search for items matching the above criteria">';
print '<a href="', $cgi_url, '">[reset the scoring criteria]</a>';
print '</form>';

if ($valid) {
  print '<hr>';
  &print_results ('the scoring criteria above', $n, $scoresort);
}
&print_trailer ();
# end of XXComplexSearchPathXX
