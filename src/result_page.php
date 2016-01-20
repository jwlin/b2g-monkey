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
<script type="text/javascript" src="result_page.js"></script>
<link rel=stylesheet type="text/css" href="result_page.css">
<meta charset="UTF-8">
</head>
	<body bgcolor="ffffcc">
	<div id="button_container">
		<a href="logout.php"><img src="img/logout-button.png"/></a>
		<a href="start.php"><img src="img/newtask-button.png"/></a>
		<h1 >結果</h1>
		<?php
			$dirName = $_SESSION['dirname'];
			echo "<input type=\"hidden\" class=\"session_text\" id=\"hidden_dirname\" name=\"hidden_dirname\" value=\"".$dirName."\" readonly>";
			echo "測試目標網址:<input type=\"text\" class=\"session_text\" id=\"url\" name=\"url\" value=\"".$_SESSION['url']."\" readonly> ";
		?>
		<br>
	</div>

	<div id="download_container">
		數值變異方式 : 
		<select id="mutaton_select" name="mutaton_select" >
			<option value="1" selected="selected">全部欄位變異</option>
			<option value="3">個別欄位變異</option>
		</select>
		數值變異種類 : 
		<select id="mutaton_mode" name="mutaton_mode" >
			<option value="1" selected="selected">Empty</option>
			<option value="2">Max Length</option>
			<option value="3">Random String</option>
			<option value="4">Malformed Symbol</option>
			<option value="5">SQL Injection</option>
		</select>
		變異路徑最大數量 : 
		<input type="number" value="5"  min="1" max="100" id="mutation_max" name="mutation_max" style="width: 40px;">
		<br><br>

		<marquee   scrollamount="5"  id="marquee"><font id="marquee_string">資料處理中,請耐心等候,感謝您!</font></marquee>
   		<a id="iframe" class="disable link" href= <?php echo "\"../python/trace/".$dirName."/state.html\"" ?> target="_blank">顯示完整結構圖</a>
   		<input type="button" value="顯示全部路徑" onclick="showAllTrace()" >
   		<input type="button" value="隱藏無Input路徑" onclick="HideNoInputTrace()" >

   		<table  class="disable"id="state_information" border="1"  align="center" ></table>
   		<form id="send_id_to_mutation" action="mutation_result.php" target="_blank" method="POST">
   			<input type="hidden" id="send_select_id" name="send_select_id" value="">
   			<input type="hidden" id="send_select_mode" name="send_select_mode" value="">
   			<input type="hidden" id="send_select_id_text" name="send_select_id_text" value="">
   			<input type="hidden" id="send_select_mode_text" name="send_select_mode_text" value="">
   			<input type="hidden" id="send_trace_number" name="send_trace_number" value="">
   			<input type="hidden" id="send_dirname" name="send_dirname" value="">
   		</form>

	</div>
	<div id="error_debug"> <div>

</body>
</html>