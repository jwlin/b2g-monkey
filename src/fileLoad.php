<!doctype html>
<html>
  <head> 
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>UpLoading file</title>
  </head>
  <body>
<?php  

  $upload_dir='/var/www/webTesting/upload/';
  echo 'uploading...'.'<br>';
  
  if($_FILES['uploadFile']['error'] == UPLOAD_ERR_OK ) {
    $fname = iconv("utf-8", "big5", $_FILES['uploadFile']['name'] );
    $uploadfile = $upload_dir.basename($fname);
    echo iconv("big5","utf-8",$fname).'<br>';
    
    if( move_uploaded_file( $_FILES['uploadFile']['tmp_name'], $uploadfile ) ) {
      echo 'upload file success!'.'<br>';
    }
    else{  
	  echo 'move file FAILED!!'.'<br>';
      print_r($_FILES);
	}
  }
  else{ echo 'upload file FAILED!!';}
  

  $list = scandir($upload_dir);
  echo '<table>';
  foreach( $list as $entry ) {
    if( is_file($upload_dir.$entry) ){
      echo '<tr><td>'.iconv("big5","utf-8",$entry).'</td><td>'.filesize($upload_dir.$entry).' byte </td></tr>';
	}
  }
  echo '</table>';
  
?>

    <form>
      <input type ="button" onclick="history.back()" value='back'>
	</form>
  </body>
</html>