<?php   
  session_start();
  $return = array();

  $dirname = $_POST['dirname'];
  $_SESSION['dirname'] = $dirname;
  $_SESSION['url'] = "";
  $dir_location = '/var/www/python/trace/'.$dirname;
  $end_location = '/var/www/python/trace/'.$dirname.'/end.json';
  $config = '/var/www/python/trace/'.$dirname.'/config.json';

  if( file_exists($dir_location) ){
    $return['exist'] = TRUE;
    if( file_exists($end_location) ){

      $end = json_decode(file_get_contents($end_location), true);

      if( $end['complete'] ){

        $return['complete'] = TRUE;
        $config_json = json_decode(file_get_contents($config), true);
        $url = $config_json['url'];
        $_SESSION['url'] = $url;

      }else{
        $return['complete'] = FALSE;
      }

    }else{
      $return['complete'] = FALSE;
    }

  }else{
    $return['exist'] = FALSE;
  }

  echo json_encode($return);
?>