<%
#<!-- $Id: cust_credit_bill.cgi,v 1.2 2001-12-18 19:30:31 ivan Exp $ -->

use strict;
use vars qw( $cgi $custnum $crednum $new $error );
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use FS::UID qw(cgisuidsetup getotaker);
use FS::CGI qw(popurl);
use FS::Record qw(qsearchs fields);
use FS::cust_credit;
use FS::cust_credit_bill;
use FS::cust_refund;
use FS::cust_main;

$cgi = new CGI;
cgisuidsetup($cgi);

$cgi->param('crednum') =~ /^(\d*)$/ or die "Illegal crednum!";
$crednum = $1;

my $cust_credit = qsearchs('cust_credit', { 'crednum' => $crednum } )
  or die "No such crednum";

my $cust_main = qsearchs('cust_main', { 'custnum' => $cust_credit->custnum } )
  or die "Bogus credit:  not attached to customer";

my $custnum = $cust_main->custnum;

if ($cgi->param('invnum') =~ /^Refund$/) {
  $new = new FS::cust_refund ( {
    'reason'  => $cust_credit->reason,
    'refund'  => $cgi->param('amount'),
    'payby'   => 'BILL',
    '_date'   => $cgi->param('_date'),
    'payinfo' => 'Cash',
    'crednum' => $crednum,
  } );
} else {
  $new = new FS::cust_credit_bill ( {
    map {
      $_, scalar($cgi->param($_));
    #} qw(custnum _date amount invnum)
    } fields('cust_credit_bill')
  } );
}

$error=$new->insert;

if ( $error ) {
  $cgi->param('error', $error);
  print $cgi->redirect(popurl(2). "cust_credit_bill.cgi?". $cgi->query_string );
} else {
  print $cgi->redirect(popurl(3). "view/cust_main.cgi?$custnum");
}


%>
