<?php
$fileDir = $_POST['dirname'];
$file = $fileDir.'.zip';

if( !file_exists($file)) {
$cmd = 'cd /var/www/webTesting/output/ && zip -r '.$file.' '.$fileDir;
$run = exec($cmd, $out, $er);
}

if (file_exists($file)) {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename='.basename($file));
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($file));
    readfile($file);
    exit;
}else{
    echo 'download Failed!!';
}
exit
?>