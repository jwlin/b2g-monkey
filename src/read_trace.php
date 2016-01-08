<?php
$dir_location = "../python/trace/"+$_POST['dirname']+"/traces.json";
$data = file_get_contents($dir_location);
$trace = json_decode($data);
echo json_encode($trace,JSON_UNESCAPED_UNICODE);
?>