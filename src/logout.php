<?php
	session_start();
	session_destroy();
	echo '<meta http-equiv=REFRESH CONTENT=0;url=login.php>';
?>