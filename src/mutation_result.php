<?php
session_start();
?>
<?php
	if($_SESSION['user_account']==null)
    { // 如果no登入過，則直接轉到登入頁面
    	echo '<meta http-equiv=REFRESH CONTENT=0;url=login.php>';
    }
?>
<html>
<head>
<script src="http://code.jquery.com/jquery-latest.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery.form/3.51/jquery.form.min.js"></script>
<script type="text/javascript" src="mutation_result.js"></script>
<link rel=stylesheet type="text/css" href="mutation_result.css">
<meta charset="UTF-8">
</head>
<body bgcolor="ffffcc">
<a href="logout.php"><img src="img/logout-button.png" /></a>
<div id="text_container">
	<h1 id="h1">數值變異結果</h1>
<?php
echo "<input type=\"hidden\"  class=\"\" id=\"hidden_select_id\" name=\"\" value=\"".$_POST['send_select_id']."\" readonly>";
echo "<input type=\"hidden\"  class=\"\" id=\"hidden_trace_number\" name=\"\" value=\"".$_POST['send_trace_number']."\" readonly>";
echo "<input type=\"hidden\"  class=\"\" id=\"hidden_dirname\" name=\"\" value=\"".$_POST['send_dirname']."\" readonly>";
echo "<h2 >資料夾 : ".$_POST['send_dirname']."  ，第".$_POST['send_trace_number']."個路徑 </h2>";
echo "<h2 >數值變異方式 : <span id=\"method\">".$_POST['send_select_id_text']."</span></h2>";
echo "<h2 >數值變異種類 : <span id=\"mode\">".$_POST['send_select_mode_text']."</span></h2>";
?>
</div>
<div id="mutation_result_container">
	<marquee   scrollamount="5"  id="marquee"><font id="marquee_string">資料處理中,請耐心等候,感謝您!</font></marquee>
<div id="error_debug"> </div>
</div>
</body>

