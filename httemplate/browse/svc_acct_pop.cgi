<%
#<!-- $Id: svc_acct_pop.cgi,v 1.5 2001-10-26 10:24:56 ivan Exp $ -->

use strict;
use vars qw( $cgi $p $svc_acct_pop );
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use FS::UID qw(cgisuidsetup);
use FS::Record qw(qsearch qsearchs);
use FS::CGI qw(header menubar table popurl);
use FS::svc_acct_pop;

$cgi = new CGI;

&cgisuidsetup($cgi);

$p = popurl(2);

print $cgi->header( @FS::CGI::header ), header('POP Listing', menubar(
  'Main Menu' => $p,
)), "Points of Presence<BR><BR>", &table(), <<END;
      <TR>
        <TH></TH>
        <TH>City</TH>
        <TH>State</TH>
        <TH>Area code</TH>
        <TH>Exchange</TH>
        <TH>Local</TH>
      </TR>
END

foreach $svc_acct_pop ( sort { 
  #$a->getfield('popnum') <=> $b->getfield('popnum')
  $a->state cmp $b->state || $a->city cmp $b->city
    || $a->ac <=> $b->ac || $a->exch <=> $b->exch || $a->loc <=> $b->loc
} qsearch('svc_acct_pop',{}) ) {
  my($hashref)=$svc_acct_pop->hashref;
  print <<END;
      <TR>
        <TD><A HREF="${p}edit/svc_acct_pop.cgi?$hashref->{popnum}">
          $hashref->{popnum}</A></TD>
        <TD><A HREF="${p}edit/svc_acct_pop.cgi?$hashref->{popnum}">
          $hashref->{city}</A></TD>
        <TD><A HREF="${p}edit/svc_acct_pop.cgi?$hashref->{popnum}">
          $hashref->{state}</A></TD>
        <TD><A HREF="${p}edit/svc_acct_pop.cgi?$hashref->{popnum}">
          $hashref->{ac}</A></TD>
        <TD><A HREF="${p}edit/svc_acct_pop.cgi?$hashref->{popnum}">
          $hashref->{exch}</A></TD>
        <TD><A HREF="${p}edit/svc_acct_pop.cgi?$hashref->{popnum}">
          $hashref->{loc}</A></TD>
      </TR>
END

}

print <<END;
      <TR>
        <TD COLSPAN=5><A HREF="${p}edit/svc_acct_pop.cgi"><I>Add new POP</I></A></TD>
      </TR>
    </TABLE>
    </CENTER>
  </BODY>
</HTML>
END

%>
