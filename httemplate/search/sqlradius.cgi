<%= include( '/elements/header.html', 'RADIUS Sessions',
             include('/elements/menubar.html',
                       'Main menu' => $p, # popurl(2),
                    ),

    )
%>

<%
  ###
  # parse cgi params
  ###

  #sort of false laziness w/cust_pay.cgi
  my $beginning = '';
  my $ending = '';
  if ( $cgi->param('beginning')
       && $cgi->param('beginning') =~ /^([ 0-9\-\/]{0,10})$/ ) {
    $beginning = str2time($1);
  }
  if ( $cgi->param('ending')
       && $cgi->param('ending') =~ /^([ 0-9\-\/]{0,10})$/ ) {
    $ending = str2time($1) + 86399;
  }
  if ( $cgi->param('begin') && $cgi->param('begin') =~ /^(\d+)$/ ) {
    $beginning = $1;
  }
  if ( $cgi->param('end') && $cgi->param('end') =~ /^(\d+)$/ ) {
    $ending = $1;
  }

  my $cgi_svc_acct = '';
  if ( $cgi->param('svcnum') =~ /^(\d+)$/ ) {
    $cgi_svc_acct = qsearchs( 'svc_acct', { 'svcnum' => $1 } );
  } elsif ( $cgi->param('username') =~ /^([^@]+)\@([^@]+)$/ ) {
    my %search = { 'username' => $1 };
    my $svc_domain = qsearchs('svc_domain', { 'domain' => $2 } );
    if ( $svc_domain ) {
      $search{'domsvc'} = $svc_domain->svcnum;
    } else {
      delete $search{'username'};
    }
    $cgi_svc_acct = qsearchs( 'svc_acct', \%search )
      if keys %search;
  } elsif ( $cgi->param('username') =~ /^(.+)$/ ) {
    $cgi_svc_acct = qsearchs( 'svc_acct', { 'username' => $1 } );
  }

  my $ip = '';
  if ( $cgi->param('ip') =~ /^((\d+\.){3}\d+)$/ ) {
    $ip = $1;
  }

  ###
  # field formatting subroutines
  ###

  my %user2svc_acct = ();
  my $user_format = sub {
    my ( $user, $session, $part_export ) = @_;

    my $svc_acct = '';
    if ( exists $user2svc_acct{$user} ) {
      $svc_acct = $user2svc_acct{$user};
    } else {
      my %search = ();
      if ( $part_export->exporrtype eq 'sqlradius_withdomain' ) {
        my $domain;
        if ( $user =~ /^([^@]+)\@([^@]+)$/ ) {
         $search{'username'} = $1;
         $domain = $2;
       } else {
         $search{'username'} = $user;
         $domain = $session->{'realm'};
       }
       my $svc_domain = qsearchs('svc_domain', { 'domain' => $domain } );
       if ( $svc_domain ) {
         $search{'domsvc'} = $svc_domain->svcnum;
       } else {
         delete $search{'username'};
       }
      } elsif ( $part_export->exporttype eq 'sqlradius' ) {
        $search{'username'} = $user;
      } else {
        die "guru meditation #420";
      }
      if ( keys %search ) {
        my @svc_acct =
          grep { qsearchs( 'export_svc', {
                   'exportnum' => $part_export->exportnum,
                   'svcpart'   => $_->cust_svc->svcpart,
                 } )
               } qsearch( 'svc_acct', \%search );
        if ( @svc_acct ) {
          warn 'multiple svc_acct records for user $user found; '.
               'using first arbitrarily'
            if scalar(@svc_acct) > 1;
          $user2svc_acct{$user} = $svc_acct = shift @svc_acct;
        }
      } 
    }

    if ( $svc_acct ) { 
      my $svcnum = $svc_acct->svcnum;
      qq(<A HREF="${p}view/svc_acct.cgi?$svcnum"><B>$user</B></A>);
    } else {
      "<B>$user</B>";
    }

  };

  my $customer_format = sub {
    my( $unused, $session ) = @_;
    return '&nbsp;' unless exists $user2svc_acct{$session->{'username'}};
    my $svc_acct = $user2svc_acct{$session->{'username'}};
    my $cust_pkg = $svc_acct->cust_svc->cust_pkg;
    return '&nbsp;' unless $cust_pkg;
    my $cust_main = $cust_pkg->cust_main;

    qq!<A HREF="${p}view/cust_main.cgi?!. $cust_main->custnum. '">'.
      $cust_pkg->cust_main->name. '</A>';
  };

  my $time_format = sub {
    my $time = shift;
    $time > 0
      ? time2str('%T%P&nbsp;%a&nbsp;%b&nbsp;%o&nbsp;%Y', $time )
      : '&nbsp;';
  };

  my $duration_format = sub {
    my $seconds = shift;
    my $hour = int($seconds/3600);
    my $min = int( ($seconds%3600) / 60 );
    my $sec = $seconds%60;
    '<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0>'.
    '<TR><TD ALIGN="right">'.
       ( $hour ? "<B>$hour</B>h" : '&nbsp;' ).
     '</TD><TD ALIGN="right">'.
       ( ( $hour || $min ) ? "<B>$min</B>m" : '&nbsp;' ).
     '</TD><TD ALIGN="right">'.
       "<B>$sec</B>s".
    '</TD></TR></TABLE>';
  };

  my $octets_format = sub {
    my $octets = shift;
    my $megs = $octets / 1048576;
    sprintf('<B>%.3f</B>&nbsp;megs', $megs);
    #my $gigs = $octets / 1073741824
    #sprintf('<B>%.3f</B> gigabytes', $gigs);
  };

  ###
  # the fields
  ###

  tie my %fields, 'Tie::IxHash', 
    'username'          => {
                             name    => 'User',
                             attrib  => 'UserName',
                             fmt     => $user_format,
                           },
    'realm'             => {
                             name    => 'Realm',
                             attrib  => 'Realm',
                           },
    'dummy'             => {
                             name    => 'Customer',
                             attrib  => '',
                             fmt     => $customer_format,
                           },
    'framedipaddress'   => {
                             name    => 'IP Address',
                             attrib  => 'Framed-IP-Address',
                             fmt     => sub { my $ip = shift;
                                              length($ip) ? $ip : '&nbsp';
                                            },
                           },
    'acctstarttime'     => {
                             name    => 'Start time',
                             attrib  => 'Acct-Start-Time',
                             fmt     => $time_format,
                           },
    'acctstoptime'      => {
                             name    => 'End time',
                             attrib  => 'Acct-Stop-Time',
                             fmt     => $time_format,
                           },
    'acctsessiontime'   => {
                             name    => 'Duration',
                             attrib  => 'Acct-Session-Time',
                             fmt     => $duration_format,
                           },
    'acctinputoctets'   => {
                             name    => 'Upload', # (from user)',
                             attrib  => 'Acct-Input-Octets',
                             fmt     => $octets_format,
                           },
    'acctoutputoctets'  => {
                             name    => 'Download', # (to user)',
                             attrib  => 'Acct-Output-Octets',
                             fmt     => $octets_format,
                           },
  ;
  $fields{$_}->{fmt} ||= sub { length($_[0]) ? shift : '&nbsp'; }
    foreach keys %fields;

  ###
  # and finally, display the thing
  ### 

  foreach my $part_export ( map $_->rebless, 
    qsearch( 'part_export', { 'exporttype' => 'sqlradius' } ),
    qsearch( 'part_export', { 'exporttype' => 'sqlradius_withdomain' } )
  ) {
    %user2svc_acct = ();
%>

<%= $part_export->exporttype %> to <%= $part_export->machine %><BR>
<%= include( '/elements/table.html' ) %>
<TR>
  <% foreach my $field ( keys %fields ) { %>
    <TH>
      <%= $fields{$field}->{name} %><BR>
      <FONT SIZE=-1><%= $fields{$field}->{attrib} %></FONT>
    </TH>
  <% } %>
</TR>
<% foreach my $session (
  @{ $part_export->usage_sessions( $beginning, $ending, $cgi_svc_acct, $ip ) }
) { %>
  <TR>
    <% foreach my $field ( keys %fields ) { %>
      <TD ALIGN="right">
        <%= &{ $fields{$field}->{fmt} }( $session->{$field},
                                         $session,
                                         $part_export,
                                       )
        %>
      </TD>
    <% } %>
  </TR>
<% } %>

</TABLE>
<BR><BR>

<% } %>
