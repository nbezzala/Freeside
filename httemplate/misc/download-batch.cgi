<%

my $conf=new FS::Conf;

#http_header('Content-Type' => 'text/comma-separated-values' ); #IE chokes
http_header('Content-Type' => 'text/plain' );

#need default
my $formatconfig = "batchconfig".$cgi->param('format');

die "No batch configuration exists.\n$formatconfig\n" unless $conf->exists($formatconfig);
my $format = $conf->config($formatconfig);

my $oldAutoCommit = $FS::UID::AutoCommit;
local $FS::UID::AutoCommit = 0;
my $dbh = dbh;

my $pay_batch = qsearchs('pay_batch', {'status'=>''} );
die "No pending batch. \n" unless $pay_batch;

my %batchhash = $pay_batch->hash;
$batchhash{'status'} = 'I';
my $new = new FS::pay_batch \%batchhash;
my $error = $new->replace($pay_batch);
die "error updating batch status: $error\n" if $error;

my $batchtotal=0;
my $batchcount=0;

my (@date)=localtime();
my $jdate = sprintf("%03d", $date[5] % 100).sprintf("%03d", $date[7]);

if ($format eq "BoM") {
  my($reformat,$origid,$datacenter,$typecode,$shortname,$longname,$mybank,$myacct) = $conf->config('batchconfig');
  printf "A%10s%04u%06u%05u%54s\n",$origid,$pay_batch->batchnum,$jdate,$datacenter,"";
  printf "XD%03u%06u%-15s%-30s%09u%-12s   \n",$typecode,$jdate,$shortname,$longname,$mybank,$myacct;
}elsif ($format eq "CSV file for TD Canada Trust Merchant PC Batch"){
  1;
}else{
  die "Unknown format for batch in batchconfig. \n";
}


for my $cust_pay_batch ( sort { $a->paybatchnum <=> $b->paybatchnum }
                           qsearch('cust_pay_batch',
			      {'batchnum'=>$pay_batch->batchnum} )
) {

$cust_pay_batch->exp =~ /^\d{2}(\d{2})[\/\-](\d+)[\/\-]\d+$/;
my( $mon, $y ) = ( $2, $1 );
$mon = "0$mon" if $mon < 10;
my $exp = "$mon$y";
$batchcount++;
$batchtotal += $cust_pay_batch->amount;

if ($format eq "BoM") {
  my( $account, $aba ) = split( '@', $cust_pay_batch->payinfo );
  printf "D%010u%09u%-12s%-29s%-19s\n",$cust_pay_batch->amount*100,$aba,$account,$cust_pay_batch->payname,$cust_pay_batch->invnum;
}elsif ($format eq "CSV file for TD Canada Trust Merchant PC Batch"){
%>,,,,<%= $cust_pay_batch->payinfo %>,<%= $exp %>,<%= $cust_pay_batch->amount %>,<%= $cust_pay_batch->paybatchnum %>
<% }else{
   die "I'm already dead, but you did not know that.\n";
}

}

if ($format eq "BoM") {
  printf "YD%08u%014u%56s\n",$batchcount,$batchtotal*100,"";
  printf "Z%014u%05u%014u%05u%41s\n",$batchtotal*100,$batchcount,"0","0","";
}elsif ($format eq "CSV file for TD Canada Trust Merchant PC Batch"){
  1;
} else{
  die "I'm already dead (again), but you did not know that.\n";
}

$dbh->commit or die $dbh->errstr if $oldAutoCommit;

%>

