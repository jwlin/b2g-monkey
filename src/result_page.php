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
		<h1 >測試結果</h1>
		<?php
			$dirName = $_SESSION['dirname'];
			echo "<input type=\"hidden\" class=\"session_text\" id=\"hidden_dirname\" name=\"hidden_dirname\" value=\"".$dirName."\" readonly>";
			echo "測試目標網址:<input type=\"text\" class=\"session_text\" id=\"url\" name=\"url\" value=\"".$_SESSION['url']."\" readonly> ";
		?>
		<br>
	</div>

	<div id="download_container">
		<marquee   scrollamount="5"  id="marquee"><font id="marquee_string">資料處理中,請耐心等候,感謝您!</font></marquee>
		<div id="iframe" class="disable">
   			<br><br>
   			<input type="button" class="show_button" value="顯示全部測試路徑" onclick="showAllTrace()" >
   			<input type="button" class="show_button" value="只顯示含動態頁面(有input欄位)的路徑" onclick="HideNoInputTrace()" >
			<br><br>
   		</div>

   		<table  class="disable information" id="state_information" border="1" align="center" cellpadding="15">
   			<tr>
   				<th>
   					自動化產生測試路徑
   				</th>
   				<th>
   					Jmeter效能測試
   				</th>
   				<th>
   					變異數值測試
   				</th>
   			</tr>
   			<tr>
   				<td>
   					<p>列表出從起點網址找出的所有測試路徑</p>
					<ul>
						<li>
							每一個路徑都列出起始點和終點的網頁號碼<br>
							及路徑的長度
						</li>
						<li>
							按下查看細節鈕，可在下方展開表格，查看<br>
							路徑每一步驟的細節。例如：網址、截圖<br>
							和點擊物件
						</li>
					</ul>
   					<div style="text-align: center;" >
   						<a href= <?php echo "\"../python/trace/".$dirName."/state.html\"" ?> target="_blank">顯示完整結構圖</a>
   					</div>
   				</td>
   				<td>
   					<p>選擇一條自動產生的路徑進行效能測試</p>
					<ul>
						<li>
							按下載檔案，將選擇的測試路徑<br>
							製作成jmeter檔案並下載到自己的<br>
							電腦上
						</li>
						<li>
							按下傳送至測試平台按鈕，將測試<br>
							路徑製作成jmeter檔案，並將連結至<br>
							效能測試頁面開始效能測試
						</li>
					</ul>
   				</td>
   				<td>
   					<p>將路徑中的input欄位變異來進行測試</p>
					<ul>
						<li>
							點選下拉選單，選擇想要的數值變異方式和<br>
							需要測試的數量上限
						</li>
						<li>
							按下開始變異測試鈕，連結至變異測試結果<br>
							頁面開始測試
						</li>
						<li>
							按下檢視測試結果鈕，可直接觀看以前做過的<br>
							變異數值測試結果
						</li>
					</ul>
   					<div style="text-align: center;" >
						數值變異方式 : 
						<select id="mutaton_select" name="mutaton_select" >
							<option value="1" selected="selected">全部欄位變異</option>
							<option value="3">個別欄位變異</option>
						</select>
						<br>
						變異測試數量上限 : 最多
						<input type="number" value="5"  min="1" max="100" id="mutation_max" name="mutation_max" style="width: 40px;">
						條
					</div>
   				</td>
   			</tr>
   		</table>
   		<form id="send_id_to_mutation" action="mutation_result.php" target="_blank" method="POST">
   			<input type="hidden" id="send_select_id" name="send_select_id" value="">
   			<input type="hidden" id="send_select_id_text" name="send_select_id_text" value="">
   			<input type="hidden" id="send_trace_number" name="send_trace_number" value="">
   			<input type="hidden" id="send_dirname" name="send_dirname" value="">
   		</form>
   		<form id="download_form" action="download.php" method="POST">
			<input id="download_filename" name="filename" type="hidden" value="">
		</form> 
		<form id="sendfile_form" action="sendfile.php" method="POST">
			<input id="sendfile_filename" name="filename" type="hidden" value="">
			<input id="sendfile_timedir" name="timedir" type="hidden" value="">
			<input id="sendfile_fname" name="fname" type="hidden" value="">
		</form>

	</div>
	<div id="error_debug"> <div>

</body>
</html>