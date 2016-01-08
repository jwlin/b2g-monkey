<?php
$dirname = $_POST['dirname'];
if(file_exists($dirname))
{
	if( is_dir($dirname) ){
		removeDirectory($dirname);
		echo "delete directory:".$dirname;
	}else{
		unlink($dirname);
		echo "delete file:".$dirname;
	}
}
else
{
	echo "file not exist";
} 
   
function removeDirectory($path) {
 	$files = glob($path . '/*');
	foreach ($files as $file) {
		if( is_dir($file) ){
			removeDirectory($file);
		}else{
			unlink($file);
		}
	}
	rmdir($path);
 	return;
}  
?>

<form action="delete.php" method="POST">
	<input type="text" style="width:400px" name="dirname">
	<input type="submit">
</form>