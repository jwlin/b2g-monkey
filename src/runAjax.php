<?php   
  session_start();
  include("mysqlInc.php");
  $return = array();

  $basename = 'testOut';
  $num = date("_ymd-h:i:s");
  $dirName = $basename.$num;
  $_SESSION['dirname'] = $dirName;
  $return['dirname'] = $dirName;

  $sql = "SELECT working FROM user WHERE user_account='".$_SESSION['user_account']."'";
  $result = mysql_query($sql);
  $row = mysql_fetch_array($result);
  $return['sql'] = mysql_error();
  $return['result'] = $row;

  if( $row['working']=='idle' ){
    $return['to_work'] = TRUE;

    $sql="INSERT INTO user_dir (user_account,user_dirname) VALUES ('".$_SESSION['user_account']."','".$_SESSION['dirname']."')";
    $result = mysql_query($sql);
    $return['sql'] = mysql_error();

    $sql="UPDATE user SET working = 'busy', last_dir = '".$_SESSION['dirname']."' WHERE user_account = '".$_SESSION['user_account']."'";
    $result = mysql_query($sql);
    $return['sql'] = mysql_error();

    // default crawl mode=1, mutant crawl mode=2
    $mode = '1';
    // base folder path = python/trace 
    $folderpath = '/var/www/python/trace';
    $cmd = 'cd /var/www/python && python controller.py '.$mode.' '.$_POST['submit_sql_id'].' '.$folderpath.' '.$dirName.' > /dev/null 2>/dev/null &';
    $run = shell_exec( $cmd );
    
    $return['sql'] = mysql_error();
    $return['folderpath'] = $folderpath;
    $return['run'] = $run;
    $return['cmd'] = $cmd;

    echo json_encode($return, JSON_UNESCAPED_UNICODE);
  }else{
    $return['to_work'] = FALSE;
    echo json_encode($return, JSON_UNESCAPED_UNICODE);
  }

  
?>