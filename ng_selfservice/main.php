<? $title ='My Account'; include('elements/header.php'); ?>
<? $current_menu = 'main.php'; include('elements/menu.php'); ?>
<?

$customer_info = $freeside->customer_info_short( array(
  'session_id' => $_COOKIE['session_id'],
) );


if ( isset($customer_info['error']) && $customer_info['error'] ) {
  $error = $customer_info['error'];
  header('Location:index.php?error='. urlencode($error));
  die();
}

extract($customer_info);

?>

<P>Hello <? echo htmlspecialchars($name); ?></P>

<? if ( $signupdate_pretty ) { ?>
  <P>Thank you for being a customer since <? echo $signupdate_pretty; ?></P>
<? } ?>

<P>Your current balance is: <B>$<? echo $balance ?></B></P>

<? echo $announcement ?>

<!--
your open invoices if you have any & payment link if you have one.  more insistant if you're late?
<BR><BR>

your tickets.  some notification if there's new responses since your last login 
<BR><BR>

anything else?
-->

<? include('elements/menu_footer.php'); ?>
<? include('elements/footer.php'); ?>
