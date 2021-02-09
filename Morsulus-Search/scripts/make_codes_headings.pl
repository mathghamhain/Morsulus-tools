use strict;
use warnings;

my %categories;
my %xrefs; # keys and values are category_names
my %alsos;
my %feature_sets;


### Parse Category File

open (CATS, "my.cat") || die "cannot open my.cat";

while (<CATS>) {	
	chomp;
	
	if ( /^[#]/ ) {
	    next; # skip comments
	}

    # Feature
	if ( /^[|](\w+):(.*)/ ) {
        my ( $set, $feature ) = ( $1, $2 );
        ( $feature, my @relationships ) = split /(?=[=<])/, $feature;
        push @{ $feature_sets{ $set } }, { feature => $feature, relationships => \@relationships };
		next;
    }
	
    # Cross-reference
	if ( /^(.+) - see (also )?(.+)/ ) {
		my ($from, $to) = ($1, $3);
        my @to = split(/ and /, $to);
        if ( $2 ) {
    		push @{$alsos{$from}}, @to;
        } else {
            foreach ( @to ) {
        		push @{$xrefs{$_}}, $from;
            }
        }
		next;
	}
	
	# otherwise a heading
	my ($category, $heading) = split(/[|]/, $_);
	$categories{$category} = $heading;
    # print "$heading - $category\n"
}

close CATS;

my @categories = sort keys %categories;


### Utilities

sub url_escape {
    local $_ = shift;
    s{([^A-Za-z0-9])}{ sprintf('%%%02X', ord ($1)) }eg;
    return $_;
}

sub html_escape {
    local $_ = shift;
    s{([^ !'()*+,./0-9:;?A-Za-z-])}{ sprintf ('&#%u;', ord($1)) }eg;
    return $_;
}

sub capitalize_words {
    local $_ = shift;
    s{(^| |[-])([a-z])}{$1\u$2}g;
    return $_;
}

sub add_optional_word_breaks {
    local $_ = shift;
    s{(....[^ a-zA-Z])([a-zA-Z])}{$1<wbr>$2}g;
    return $_;
}


### CATEGORIES

sub heading_link {
    my ( $heading, $text ) = @_;
    my $heading_q = url_escape( $heading );
    qq{<a href="XXDescSearchUrlXX?p=$heading_q">$text</a>}
}

sub find_category_heading {
    my $category_or_prefix = shift;
    my $heading = $categories{$_};
    return $heading if $heading;
    my @matches = grep { /^\Q$category_or_prefix/ } @categories;
    if ( ! @matches ) {
        warn "Can't find heading for $category_or_prefix\n";
        return;
    }
    $categories{ $matches[0] } 
}

my $table_body = join("\n", 
    "<tbody>",
    ( map { 
        my $category = $_;
        my $heading = $categories{ $category };
        my $xrefs = $xrefs{$category};
        my $alsos = $alsos{$category};
        my $heading_link = heading_link( $heading, add_optional_word_breaks($heading) );
        my $heading_escape = url_escape( $heading );
        my $category_text = capitalize_words( $category );
        my $xref_string = ( ! $xrefs ) ? '' : ' <span class="category-synonyms">(' . join('; ', map { capitalize_words($_) } @$xrefs) . ')</span>';
        my $alsos_string = ( ! $alsos ) ? '' : ' See also ' . join('; ', map { sprintf qq{<a href="#%s">%s</a>}, find_category_heading($_), capitalize_words($_) } @$alsos);
        "<tr>",
            qq{<td> $heading_link </td>},
            qq{<td> <a name="$heading"></a> $category_text $xref_string $alsos_string </td>},
        "</tr>",
    } @categories ),
    "</tbody>",
);

open (HTML, "category_codes.html") || die "cannot read category_codes.html";
my $html = join "", <HTML>;
close HTML;

$html =~ s{<tbody>.*</tbody>}{$table_body}s;

open (HTML, ">category_codes.html") || die "cannot write to category_codes.html";
print HTML $html;
close HTML;


### FEATURES

$table_body = join("\n", 
    "<tbody>",
    ( map { 
        my $feature_set = $_;
        my @features = @{ $feature_sets{ $feature_set } };
        ( 
        "<tr class='feature-set'>",
            qq{<td> $feature_set </td>},
            qq{<td></td>},
        "</tr>",            
        ),
        map {
            my $feature = $_;
            my $feature_label = html_escape( $feature->{'feature'} );
            my $relationship_html = ( $feature->{'relationships'} and @{ $feature->{'relationships'} } ) ? qq{ <span class="feature-relationships">(} . join('; ', map { html_escape($_) } @{ $feature->{'relationships'} } ) . qq{)</span>} : '';
            "<tr>",
                qq{<td>  </td>},
                qq{<td> $feature_label $relationship_html </td>},
            "</tr>",            
        } @features;
    } sort keys %feature_sets ),
    "</tbody>",
);

open (HTML, "feature_codes.html") || die "cannot read feature_codes.html";
$html = join "", <HTML>;
close HTML;

$html =~ s{<tbody>.*</tbody>}{$table_body}s;

open (HTML, ">feature_codes.html") || die "cannot write to feature_codes.html";
print HTML $html;
close HTML;


### FEATURES

$table_body = join("\n", 
    "<tbody>",
    ( map { 
        my $feature_set = $_;
        my @features = @{ $feature_sets{ $feature_set } };
        ( 
        "<tr class='feature-set'>",
            qq{<td> $feature_set </td>},
            qq{<td></td>},
        "</tr>",            
        ),
        map {
            my $feature = $_;
            my $feature_label = html_escape( $feature->{'feature'} );
            my $relationship_html = ( $feature->{'relationships'} and @{ $feature->{'relationships'} } ) ? qq{ <span class="feature-relationships">(} . join('; ', map { html_escape($_) } @{ $feature->{'relationships'} } ) . qq{)</span>} : '';
            "<tr>",
                qq{<td>  </td>},
                qq{<td> $feature_label $relationship_html </td>},
            "</tr>",            
        } @features;
    } sort keys %feature_sets ),
    "</tbody>",
);

open (HTML, "codes_features.html") || die "cannot read codes_features.html";
$html = join "", <HTML>;
close HTML;

$html =~ s{<tbody>.*</tbody>}{$table_body}s;

open (HTML, ">codes_features.html") || die "cannot write to codes_features.html";
print HTML $html;
close HTML;
