<?php
session_start();
header("Content-Type:text/html; charset=utf-8");
include("mysqlInc.php");
?>
<html>
<head>
<script src="http://code.jquery.com/jquery-latest.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery.form/3.51/jquery.form.min.js"></script>
<script type="text/javascript" src="record_page.js"></script>
<link rel=stylesheet type="text/css" href="record_page.css">
<meta charset="UTF-8">
</head>
<body bgcolor="ffffcc">
<?php
	if($_SESSION['user_account']==null)
    { // 如果no登入過，則直接轉到登入頁面
    	echo '<meta http-equiv=REFRESH CONTENT=0;url=login.php>';
    }
?>
<input type="hidden" name="choose" id="choose" value="">
<div id="container">
	<a href="logout.php"><img src="img/logout-button.png"/></a>
	<a href="start.php"><img src="img/newtask-button.png"/></a>
	<h1 >記錄</h1>
	<h1 >下方目錄是您過去的測試紀錄 點選按鈕以前往</h1>
</div>
<div id="table_container">
	<table id="record_table" border="1"  align="center">
<?php
$user_account = $_SESSION['user_account'];
$sql = "SELECT user_dirname FROM user_dir WHERE user_account='".$user_account."'";
$result = mysql_query($sql);

while($row = mysql_fetch_array($result))
{
	echo "<tr><td><input type=\"button\" value=\"".$row['user_dirname']."\" onclick=\"check_record('".$row['user_dirname']."')\"></td></tr>";
}
?>
	</table>
</div>
</body>
</html>