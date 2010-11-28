<% include('elements/svc_Common.html',
            'table'     => 'svc_dsl',
            'labels'    => \%labels,
            'fields' => \@fields,
	    'svc_callback' => $svc_cb,
	    'html_foot' => $html_foot,
          )
%>
<%init>

# XXX: AJAX auto-pull

my $fields = FS::svc_dsl->table_info->{'fields'};
my %labels = map { $_ =>  ( ref($fields->{$_})
                             ? $fields->{$_}{'label'}
                             : $fields->{$_}
                         );
                 } keys %$fields;
my @fields = keys %$fields;

my $footer;

my $html_foot = sub {
    return $footer;
};

my $svc_cb = sub {
    my( $cgi,$svc_x, $part_svc,$cust_pkg, $fields1,$opt) = @_;

    my @exports = $part_svc->part_export_dsl_pull;
    die "more than one DSL-pulling export attached to svcpart ".$part_svc->svcpart
	if ( scalar(@exports) > 1 );
    
    # if no DSL-pulling exports, then just display everything, which is the
    # default behaviour implemented above
    return if ( scalar(@exports) == 0 );

    my $export = @exports[0];
    $opt->{'disable_unprovision'} = 1;

    @fields = ( 'phonenum',
	    { field => 'loop_type', 
	      value => 'FS::part_export::'.$export->exporttype.'::loop_type_long'
	    },
	    { field => 'desired_due_date', type => 'date', },
	    { field => 'due_date', type => 'date', },
	    { field => 'pushed', type => 'datetime', },
	    { field => 'monitored', type => 'checkbox', },
	    { field => 'last_pull', type => 'datetime', },
	    'first',
	    'last',
	    'company'  );

    if($export->exporttype eq 'ikano') {
	push @fields, qw ( username password isp_chg isp_prev staticips );
    }
    # else add any other export-specific stuff here
   
    $footer = "<B>".$export->status_line($svc_x)."</B>";
    $footer .= "<BR><BR><BR>Order Notes:<BR>".$export->notes_html;
};
</%init>
