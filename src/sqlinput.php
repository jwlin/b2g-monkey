<?php
session_start();
include("mysqlInc.php");

$return = array();

if(isset($_POST['url'])&&isset($_POST['depthRange'])&&isset($_POST['runTimeRange']))
{
  $_SESSION['url'] = $_POST['url'];
  $sql = "SELECT * FROM webtesting";
  $result = mysql_query($sql);
  $id = mysql_num_rows($result)+1;
  $sql = "SELECT * FROM inputtable";
  $result = mysql_query($sql);
  $uni = mysql_num_rows($result);
  $url = $_POST['url'];
  $depthRange = $_POST['depthRange'];
  $runTimeRange = $_POST['runTimeRange'];
  $size = sizeof($_POST['inputname']);
  $inputnamearray = ($_POST['inputname']);
  $inputvaluearray = ($_POST['inputvalue']);
  $inputtypearray = ($_POST['inputtype']);
  $inputmutation = ($_POST['inputmutation']);
  $inputmutation = str_replace('\"', '"', $inputmutation);
  $inputmutationarray = json_decode($inputmutation);
    
    
  for($i=0;$i<$size;$i++)
  {        
    $temp = implode(";", $inputmutationarray[$i]);
    $temp2= $uni+$i;
    $sql = "INSERT INTO inputtable (id,name,value,type,mutation,uni) VALUES ".
            "('".$id."','".$inputnamearray[$i]."','".$inputvaluearray[$i]."','".$inputtypearray[$i]."','".$temp."','".$temp2."')"; 
    mysql_query($sql);
		
  }
  $sql = "INSERT INTO webtesting (id,url, deep, time) VALUES ('".$id."', '".$url."', '".$depthRange."', '".$runTimeRange."')";
  mysql_query($sql);
}

$return['submit_sql_id'] = $id;
echo json_encode($return, JSON_UNESCAPED_UNICODE);

?>
