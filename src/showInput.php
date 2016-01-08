<?php
  $dirname = $_POST['dirname'];
  $complete = false;
  $return = array();
  
  
  //end.html->complete
  if( file_exists($dirname.'/end.html') ){
    $complete = true;  
    	
    //list of all name of testcases
    if( file_exists($dirname.'/inputs/FindInput.json') ){	  
	  $return['inputJson'] = file_get_contents($dirname.'/inputs/FindInput.json');
		
      // Close the file that no longer in use
      fclose($file); 
	}	
  }  	  
	  
  $return['complete'] = $complete;
  echo json_encode($return, JSON_UNESCAPED_UNICODE);
?>