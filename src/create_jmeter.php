<?php
$file_location= "/var/www/python/trace/".$_POST['dirname']."/traces.json";
$dir_loacation = "/var/www/python/trace/".$_POST['dirname']."/jmeter";

#check if dir exist, if not, mkdir
if (!file_exists($dir_loacation) && !is_dir($dir_loacation)) {
    mkdir($dir_loacation);         
} 

$trace_number = (int)$_POST['trace_number'];
$cmd = 'cd /var/www/python && python path.py '.$file_location.' '.$dir_loacation.' '.$trace_number.' 1 2>&1';
$run = exec($cmd,$out,$er);

$return['out'] = $out;
$return['er']= $er;
echo json_encode($return);
?>