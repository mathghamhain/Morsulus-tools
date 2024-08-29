#!XXPerlPathXX

# This is a CGI script to do a complex search of the oanda database.
# It is to be installed at XXComplexSearchPathXX on XXServerNameXX.

# Set URL for this script.
$cgi_url = 'XXComplexSearchUrlXX';

require 'XXCommonClientPathXX';
require 'XXMyCatXX';

my %categories    = categories();
my @feature_names = feature_names();
my %feature_names = map { $_ => $_ } @feature_names;
my %xref          = xrefs();
my %heading  = map { $categories{$_}->{heading} => $_ } keys %categories;
my @validation_errors;

# Set title for form.
$form_title = 'Complex Search Form';

$criteria = 10;

# option settings

@methods = ('', 'armory description', 'name pattern', 'record type', 'blazon pattern', 'broad name', 'date and kingdom', 'notes pattern');

%methods = map { $_ => capitalize_words($_) } @methods;
$methods{''} = 'Select search type:';

@sorts = ('name only', 'last action date', 'blazon');

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
  $registered_status = $right if ($left eq 'rs');
  $raw_display_mode = $right if ($left eq 'raw');
}
$limit = 500
  if ($limit !~ /^\d+$/);
$scoresort = 1 if ( ! defined $minimum_score );
$minimum_score = 1 if ( $minimum_score !~ /^[-]?\d+$/);

&print_header ();

$invalid = 0;
$valid = 0;
$maximum_score = 0;
for $i (1 .. $criteria) {
    $weight[$i] = '1' if ( ! length $weight[$i] );
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
        my @descs = validate_descs($p[$i]);
        if (@descs != 1)
        {
            unshift @validation_errors, "Armory description matched 0 or more than 1 category:";
            unshift @validation_errors, @descs;
            unshift @validation_errors, "First match used" if @descs > 1;
        }
        $p[$i] = @descs == 0 ? $p[$i] : $descs[0];
      print S "d0 $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'blazon pattern') {
      print S "ebi $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'notes pattern') {
      print S "e5i $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'broad name') {
      print S "n $weight[$i] $p[$i]";
    } elsif ($method[$i] eq 'date and kingdom') {
      my ($date1, $date2, $klist) = split(/ /, $p[$i]);
      $klist = join('', sort keys %kingdom_name) if ($klist eq '*');
      $p[$i] = parse_date_kingdom($p[$i]);
      print S "s $weight[$i] $p[$i]";
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

print '<p>Enter one or more criteria to search for.';
print '<a href="XXComplexHintsPageUrlXX">Hints are available for this form.</a>';
  
print '<div>';
for $i (1 .. $criteria) {
  $weight[$i] = 1 if $weight[$i] eq undef;
  $method[$i] = 'armory description' unless $method[$i];
  print '<div>';

  # method selector
  &select ("m$i", $method[$i], @methods, \%methods);

  print '<input type="text" name="p', $i, '" value="', $p[$i], '" size="60" placeholder="Search pattern">';

  print '<input type="text" name="w', $i, '" value="', ( $weight[$i] == 1 ? '' : $weight[$i] ), '" size="4" placeholder="Weight">';
  print '</div>';
}
print '</div>';

  print '<input type="text" name="w', $i, '" value="', ( $weight[$i] == 1 ? '' : $weight[$i] ), '" size="6" placeholder="Weight">';
  print '</div>';
}
print '</div>';
if ($valid && @validation_errors)
{
    print '<p>Description validation errors:';
    print '<br/>', $_ for @validation_errors;
}

&display_options (1);

print '<input type="submit" value="Search">';
print '</form>';

if ($valid) {
  print '<hr>';
  &print_results ('the scoring criteria above', $n, $scoresort);
}
&print_trailer ();

sub parse_date_kingdom
{
    my ($input) = @_;
    my @parts = split(/ +/, $input);
    if (@parts == 1) # is it a date or is it a kstring
    {
        # \d{6} is a month -> <date> *
        # [A-Za-z]+ is a kstring -> <all dates> kstring
        # * -> <all dates> *
        if ($parts[0] =~ /\d+/)
        {
            @parts = ($parts[0], $parts[0], '*');
        }
        elsif ($parts[0] =~ /[A-Za-z]/)
        {
            @parts = ('196600', '209912', $parts[0]);
        }
        elsif ($parts[0] eq '*')
        {
            @parts = ('196600', '209912', '*');
        }
    }
    if (@parts == 2)
    {
        # date kstring -> date date kstring (single month)
        # date date -> date date * (date range; all kingdoms)
        if ($parts[1] =~ /\d+/)
        {
            @parts = ($parts[0], $parts[1], '*');
        }
        else
        {
            @parts = ($parts[0], $parts[0], $parts[1]);
        }
    }
    if (@parts == 3) 
    {
        $parts[0] = '196601' if $parts[0] eq '*';
        $parts[1] = '209912' if $parts[1] eq '*';
        $parts[2] = join('', sort keys %kingdom_name) if $parts[2] eq '*';
        $parts[0] = $parts[0].'01' if $parts[0] =~ /^\d{4}$/;
        $parts[1] = $parts[1].'12' if $parts[1] =~ /^\d{4}$/;
        $parts[0] = '196601' if $parts[0] lt '196600';
        $parts[1] = '196601' if $parts[1] lt '196600';
        $parts[0] = '209912' if $parts[0] gt '209912';
        $parts[1] = '209912' if $parts[1] gt '209912';
    }
    return join(' ', @parts);
}

sub validate_descs
{
    my ($descs) = @_;
    my @descs;
    for my $d (split(/[|]/, $descs))
    {
        push @descs, validate_desc($d);
    }
    return join('|', @descs);
}

sub validate_desc
{
    my ($desc) = @_;
    
    $desc =~ s/\s+/ /g;
    $desc =~ s/ $//;
    $desc =~ s/ :/:/g;
    $desc =~ s/: /:/g;
    $desc =~ s/^ //;
    
    if ($desc =~ /:/ or $desc !~ /[a-z,]/) # heading maybe with features
    {
        my ($heading, @features) = split(/:/, $desc);
        $heading = uc($heading);
        if (! exists $heading{$heading})
        {
            my $newdesc = join(', ', lc($heading), @features);
            return validate_desc($newdesc);
        }
        for my $feature (@features)
        {
            if (! exists $feature_names{$feature})
            {
                push @validation_errors, "'$feature' in '$desc' is invalid feature";
            }
        }
        return join(":", $heading, @features);
    }
    #return "falling off end";
    # otherwise category maybe with features
    
    my @features;
    
    while ($desc)
    {
        if (exists $xref{$desc})
        {
            #say "found xref(s) for $desc:";
            my @xrefs;
            for my $xref (@{$xref{$desc}})
            {
                if (!exists $categories{$xref})
                {
                    push @xrefs, validate_desc($xref);
                }
                else 
                {
                    push @xrefs, $categories{$xref}->{heading};
                }
            }
            my @descs = map { @features ? join(":", $_, join(":", @features)) : $_ } @xrefs;
            #say @descs;
            return @descs;
        }
        
        my ($front, undef, $back) = ($desc =~ /^(.*)(, )(.*?)$/);
        
        if (defined $back)
        {
            $desc = $front;
            unshift @features, $back;
        }
        else
        {
            if (exists $heading{uc($desc)})
            {
                return uc($desc);
            }
            push @validation_errors, "'$desc' is not a valid category";
            return;
        }
    }
}
# end of /home3/www/oanda.sca.org/oanda_complex.cgi
