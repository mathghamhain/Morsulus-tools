#!XXPerlPathXX

# This is a CGI script to do a name search of the oanda database.
# It is to be installed at XXNameSearchPathXX on XXServerNameXX.

# Set URL for this script.
$cgi_url = 'XXNameSearchUrlXX';

# Set title for form.
$form_title = 'Name Search Form';

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

  print S 'n 1 ', $p;
  print S 'EOF';

  $n = &get_matches ();

  $scoresort = 0;
  @matches = sort byname @matches;
}

print '<p>Enter an exact name to search for.';
print '<a href="XXNameHintsPageUrlXX">Hints are available for this form.</a>';

print '<p>Exact Name: ';
print '<input type="text" name="p" value="', $p, '" size="30">';

print '<input type="submit" value="Search">';
print '</form>';

my %stats_descriptions = (
    'armory-badge-current' => "Badges (current)",
    'armory-badge-obsolete' => "Badges (obsolete)",
    'armory-device-current' => "Devices (current)",
    'armory-device-obsolete' => "Devices (obsolete)",
    'name-personal-current' => "Personal Name (current)",
    'name-personal-obsolete' => "Personal Name (obsolete)",
    'name-personal-change' => "Personal Name (change)",
    'name-nonpersonal-current' => "Non-personal Name (current)",
    'name-nonpersonal-obsolete' => "Non-personal Name (obsolete)",
    'name-nonpersonal-change' => "Non-personal Name (change)",
);

if ($p ne '') {
  print '<hr>';
  &print_results ('name="<i>'.&escape($p).'</i>"', $n, $scoresort, 1);

  if ($n) {
    my $name_total_current = $result_stats{'name-personal-current'} + $result_stats{'name-nonpersonal-current'};
    my $armory_total_current = $result_stats{'armory-badge-current'} + $result_stats{'armory-device-current'};
    print "<p><b>Total Registrations: $name_total_current Names, $armory_total_current Armory</b>";
    print "<ul>";
    foreach ( sort keys %result_stats ) {
      print "<li> " . ( /total/ ? '<b>' : '' ) . ( $stats_descriptions{$_} || $_ ) . ": $result_stats{ $_ }" . ( /total/ ? '</b>' : '' );
    }
    print "</ul>";
  }

  if ($n == 0) {
    # No matches.  Make suggestions.
    local ($you, $pp, $without, $in);

    $you = '<p>You';
    $pp = $p;
    if ($p =~ /["]/) {
      print $you, ' typed something in quotes.';
      $pp =~ tr/"//d;
      $without = ' without the quotes';
      $you = 'You also';
    }
    if ($pp !~ /[A-Z]/) {
      print $you, ' typed the name entirely in lower case.';
      $in = 'in';
      $you = 'You also';
    } elsif ($pp !~ /[a-z]/) {
      print $you, ' typed the name entirely in UPPER CASE.';
      $in = 'in';
      $you = 'You also';
    } elsif ($pp =~ /^[a-z]/) {
      print $you, ' typed the name with a lower case initial.';
      $in = 'in';
      $you = 'You also';
    }
    if ($pp =~ /[*?\\]/) {
      print $you, ' typed something that looked like a wildcard.';
      print 'Perhaps you should try a';
      print '<a href="XXNpSearchUrlXX?a=', $arm_descs,
        '&b=broad&c=case-', $in, 'sensitive&d=', $era, '&g=', $gloss_links,
        '&l=500&p=', &encode ($pp), '&s=name+only">',
        'case-', $in, 'sensitive pattern search', $without, '</a>.';
    } elsif ($pp !~ /\s/) {
      print $you, ' typed only one word of the name.';
      print 'Perhaps you would like to see';
      print '<a href="XXNpSearchUrlXX?a=', $arm_descs,
        '&b=broad&c=case-', $in, 'sensitive&d=', $era, '&g=', $gloss_links,
        '&l=500&p=', &encode ("\\b$pp\\b"), '&s=name+only">',
        'all names containing the word "', &escape($pp),'"</a>';
      print 'or';
      print '<a href="XXNpSearchUrlXX?a=', $arm_descs,
        '&b=broad&c=case-', $in, 'sensitive&d=', $era, '&g=', $gloss_links,
        '&l=500&p=', &encode ("^$pp"), '&s=name+only">',
        'all names beginning with "', &escape($pp),'"</a>';
    } elsif ($in ne '') {
      print 'Perhaps you should try a';
      print '<a href="XXNpSearchUrlXX?a=', $arm_descs,
        '&b=broad&c=case-insensitive&d=', $era, '&g=', $gloss_links,
        '&l=500&p=', &encode ($pp), '&s=name+only">',
        'case-insensitive pattern search', $without, '</a>.';
    } elsif ($without ne '') {
      print 'Perhaps you should';
      print '<a href="XXNameSearchUrlXX?p=', &encode ($pp), '">',
        'try again', $without, '</a>.';
    } elsif (&permute($pp) ne $pp) {
      $pp = &permute($pp);
      print 'Perhaps you should try';
      print '<a href="XXNameSearchUrlXX?p=', &encode ($pp), '">',
        &escape($pp), '</a>.';
    } elsif ($pp =~ /^([a-z][a-z]).* ([a-z])\S+$/i) {
      print 'Perhaps you should look at';
      print '<a href="XXNpSearchUrlXX?a=', $arm_descs,
        '&b=broad&c=case-insensitive&d=', $era, '&g=', $gloss_links,
        '&l=500&p=', &encode ("^$1.* $2\\S+\$"), '&s=name+only">',
        'names of the form "', $1, '... ', $2, '..."</a>.';
    }
  }

  print '<p><a href="XXComplexSearchUrlXX?a=', $arm_descs, '&d=', $era,
    '&g=', $gloss_links, '&l=500&s=name+only&w1=1&m1=broad+name',
    '&p1=', &encode ($p), '">',
    'Convert to complex search.</a>';
  # print '<p><a href="XXCorrectionUrlXX?p=', &encode($p), '">',
  # 'Request a correction of an item above.</a>';
}
&print_trailer ();
# end of XXNameSearchPathXX
