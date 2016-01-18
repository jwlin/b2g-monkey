<?php
	session_start();
	include("mysqlInc.php");

  	$return = array();
	$end_location= "/var/www/python/trace/".$_POST['dirname']."/end.json";
	$location= "/var/www/python/trace/".$_POST['dirname']."/traces.json";
	$return['location'] = $location;
	$config_location = "/var/www/python/trace/".$_POST['dirname']."/config.json";
	$mutant_location="/var/www/python/trace/".$_POST['dirname']."/mutant/*";
	if (file_exists($end_location)) {
    	$return['exist'] = TRUE;
    	$return['end'] = TRUE;

		$sql = "SELECT last_dir FROM user WHERE user_account='".$_SESSION['user_account']."'";
		$result = mysql_query($sql);
		$row = mysql_fetch_array($result);
		$return['sql'] = mysql_error();
		$return['result'] = $row;
		if($row['last_dir']==$_POST['dirname']){
			$sql="UPDATE user SET working = 'idle' WHERE user_account = '".$_SESSION['user_account']."'";
			$result = mysql_query($sql);
			$return['sql'] = mysql_error();
		}

		$end = json_decode(file_get_contents($end_location), true);
		if( $end['complete'] ){

			$config = json_decode(file_get_contents($config_location), true);
			if( $config['url'] ){
				$_SESSION['url'] = $config['url'];
				$return['url'] = $config['url'];
			}

    		if( file_exists($location) ){
    			$return['complete'] = TRUE;
				$trace = json_decode(file_get_contents($location));
				$return['json'] = $trace;
				$file = glob($mutant_location);
				$return['mutant'] = $file;
    		}else{
    			$return['complete'] = FALSE;
				$return['json'] = $end['note'];
    		}
		}
		else{
    		$return['complete'] = FALSE;
			$return['json'] = $end['note'];
		}
	} 
	else {
    	$return['exist'] = FALSE;
    	$return['end'] = FALSE;
    	$return['complete'] = FALSE;
		$return['json'] = '';
	}
	echo json_encode($return);
?>