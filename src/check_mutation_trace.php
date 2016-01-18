<?php
  	$return = array();
  	$dir_location = "/var/www/python/trace/".$_POST['dirname']."/mutant/mutant".$_POST['trace_number'];
	$end_location = "/var/www/python/trace/".$_POST['dirname']."/mutant/mutant".$_POST['trace_number']."/end.json";
	$traces_location = "/var/www/python/trace/".$_POST['dirname']."/mutant/mutant".$_POST['trace_number']."/mutation_traces.json";
	$return['location'] = $dir_location;
	if(file_exists($dir_location)){
		$return['exist'] = TRUE;

		if (file_exists($end_location)) {
			$end = json_decode(file_get_contents($end_location), true);
	    	$return['end'] = TRUE;

			if( $end['complete'] ){
	    		if( file_exists($traces_location) ){
	    			$return['complete'] = TRUE;
					$trace = json_decode(file_get_contents($traces_location));
					$return['json'] = $trace;
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
	    	$return['end'] = FALSE;
	    	$return['complete'] = FALSE;
			$return['json'] = '0';
		}
	}
	else{		
		$return['exist'] = FALSE;
    	$return['end'] = FALSE;
    	$return['complete'] = FALSE;
		$return['json'] = '0';
	}
	echo json_encode($return);
?>