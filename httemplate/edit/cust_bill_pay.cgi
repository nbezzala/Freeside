<%
#<!-- $Id: cust_bill_pay.cgi,v 1.1 2001-12-18 19:30:31 ivan Exp $ -->

use strict;
use vars qw( $cgi $query $custnum $paynum $amount $invnum $p1 $otaker ); # $reason $cust_credit );
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Date::Format;
use FS::UID qw(cgisuidsetup getotaker);
use FS::CGI qw(header popurl);
use FS::Record qw(qsearch fields);
use FS::cust_pay;
use FS::cust_bill;


$cgi = new CGI;
cgisuidsetup($cgi);

if ( $cgi->param('error') ) {
  $paynum = $cgi->param('paynum');
  $amount = $cgi->param('amount');
  $invnum = $cgi->param('invnum');
} else {
  ($query) = $cgi->keywords;
  $query =~ /^(\d+)$/;
  $paynum = $1;
  $amount = '';
  $invnum = '';
}

$otaker = getotaker;

$p1 = popurl(1);

print header("Apply Payment", '');
print qq!<FONT SIZE="+1" COLOR="#ff0000">Error: !, $cgi->param('error'),
      "</FONT><BR><BR>"
  if $cgi->param('error');
print <<END;
    <FORM ACTION="${p1}process/cust_bill_pay.cgi" METHOD=POST>
END

die unless $cust_pay = qsearchs('cust_pay', { 'paynum' => $paynum } );

my $unapplied = $cust_pay->unapplied;

print "Payment # <B>$paynum</B>".
      qq!<INPUT TYPE="hidden" NAME="paynum" VALUE="$paynum">!.
      '<BR>Date: <B>'. time2str("%D", $cust_pay->_date). '</B>'.
      '<BR>Amount: $<B>'. $cust_pay->paid. '</B>'.
      "<BR>Unapplied amount: \$<B>$unapplied</B>".
      ;

my @cust_bill = grep $_->owed != 0,
                qsearch('cust_bill', { 'custnum' => $cust_pay->custnum } );

print <<END;
<SCRIPT>
function changed(what) {
  cust_bill = what.options[what.selectedIndex].value;
END

foreach my $cust_bill ( @cust_bill ) {
  my $invnum = $cust_bill->invnum;
  my $changeto = $cust_bill->owed < $unapplied
                   ? $cust_bill->owed 
                   : $unapplied
  print <<END;
  if ( cust_bill == $invnum ) {
    what.form.amount.value = "$changeto";
  }
END
}

#print <<END;
#  if ( cust_bill == "Refund" ) {
#    what.form.amount.value = "$credited";
#  }
#}
#</SCRIPT>
#END
print "</SCRIPT>\n";

print qq!<BR>Invoice #<SELECT NAME="invnum" SIZE=1 onChange="changed(this)">!,
      '<OPTION VALUE="">';
foreach my $cust_bill ( @cust_bill ) {
  print '<OPTION'. ( $cust_bill->invnum eq $invnum ? ' SELECTED' : '' ).
        ' VALUE="'. $cust_bill->invnum. '">'. $cust_bill->invnum.
        ' -  '. time2str("%D",$cust_bill->_date).
        ' - $'. $cust_bill->owed;
}
#print qq!<OPTION VALUE="Refund">Refund!;
print "</SELECT>";

print qq!<BR>Amount \$<INPUT TYPE="text" NAME="amount" VALUE="$amount" SIZE=8 MAXLENGTH=8>!;

print <<END;
<BR>
<INPUT TYPE="submit" VALUE="Apply">
END

print <<END;

    </FORM>
  </BODY>
</HTML>
END

%>
