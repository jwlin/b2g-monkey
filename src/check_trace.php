<?php
	session_start();
	include("mysqlInc.php");

  	$return = array();
	$end_location= "/var/www/python/trace/".$_POST['dirname']."/end.json";
	$location= "/var/www/python/trace/".$_POST['dirname']."/traces.json";
	$return['location'] = $location;
	if (file_exists($end_location)) {

		$end = json_decode(file_get_contents($end_location), true);
		if( $end['complete'] ){
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

    		if( file_exists($location) ){
    			$return['complete'] = TRUE;
				$trace = json_decode(file_get_contents($location));
				$return['json'] = $trace;
		
    		}else{
    			$return['complete'] = FALSE;
				$return['json'] = $end['note'];
    		}
		}
		else{
	    	$return['end'] = TRUE;
    		$return['complete'] = FALSE;
			$return['json'] = $end['note'];
		}
	} 
	else {
    	$return['exist'] = FALSE;
    	$return['complete'] = FALSE;
		$return['json'] = '0';
	}
	echo json_encode($return, JSON_UNESCAPED_UNICODE);
?>