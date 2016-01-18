<?php

$src = '/var/www/python/trace/'.$_POST['filename'];
//$src = '/var/www/python/trace/123';

$des = $_POST["timedir"].'_'.$_POST["fname"];

$data = file_get_contents($src);

//  $client = new SoapClient("http://140.92.143.2/Axis2Prj/services/EchoTest?wsdl");
$client = new SoapClient("http://211.23.177.185/PHPRecieveProj/services/EchoTest?wsdl");


 // $path = "c:\Script.jmx";
  $result = $client->recvfile(array('data' => $data , 'path' => $des));
//  var_dump($result);

$outterArray = ((array)$result);
//echo $outterArray['return'];

if (strpos($outterArray['return'],'arrived') !== false) {
    //echo 'true';
   // header('Location: http://211.23.177.185/cloud/views/ScriptCreate/buildp.xhtml');

      header('Location: http://211.23.177.185/cloud/views/ScriptCreate/createCrawlingScript.xhtml?folderpath='.$des );

}

?>
