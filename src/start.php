<?php
	session_start();
?>
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
	<title>Start Web</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="css/bootstrap.min.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="css/bootstrap-multiselect.css" type="text/css"/>
    <script src="http://code.jquery.com/jquery-latest.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/jquery.form/3.51/jquery.form.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/ajaxfileupload.js"></script>
    <script src="js/bootstrap-multiselect.js"></script>
    <script type="text/javascript" language="javascript" ></script>	
    <script type="text/javascript" src="webtesting.js"></script>
   <!-- <script type="text/javascript">    $('#aa').multiselect();</script> -->
      
  </head>
<?php
include("mysqlInc.php");




?>
  <body>  
  	<?php
	if($_SESSION['user_account']==null)
    { // 如果no登入過，則直接轉到登入頁面
    	echo '<meta http-equiv=REFRESH CONTENT=0;url=login.php>';
    }
	?>
    <div class="container">
	  <a href="logout.php"><img src="img/logout-button.png"/></a>
      <div class="page-header">
	    <h1>Hello world!</h1>
		<h3>A Web for testing web......</h3>
      </div><!--  page-header  -->
	
  	  <h3>線上網站測試 使用說明:</h3>
	  <h5>1.使用線上表格填寫使用說明:</h5>
	  <p>     必備參數(1)測試目標網址  (2)網站測試深度  (3)最大測試時間</p>
	  <p>     若有需要設定 input 參數，請使用下方表格</p>
	  <h5>2.上傳符合規格的表單以進行測試</h5>
	  <ul class="nav nav-tabs">
        <li class="active"><a href="#form_submit_content"  data-toggle="tab" onclick="form_submit()">表格</a></li>
        <!--<li><a href="#form_upload_content"  data-toggle="tab" onclick="form_upload()">檔案</a></li> -->
      </ul><!--  nav-tabs  -->
	  
      <form class="form-horizontal" id="page_content" name="page_content" method="post" action='sqlinput.php' enctype="multipart/form-data">
      <div class="tab-content" id="my-tab-content">  
		
        <div class="tab-pane active" id="form_submit_content">
		
	      <div class="hero-unit">
		    <p></p>
		  </div><!--  hero-unit  -->
		  
  		  <h5></h5>
          <div class="control-group">
  	        <p class="control-label">測試目標網址：</p> 
		    <div class="controls">
	          <input class="input-xlarge" type="url" id="url" name="url">
		    </div>
          </div><!--  control-group  -->
          <div class="control-group">
	        <p class="control-label">網站測試深度：</p>
		    <div class="controls">
	          <input type="range" id="depthRange" name="depthRange" value="1" min="1" max="5" step="1" onchange="range_show()">
			  <span class="offset">
		      <span id="rangeValue">1</span>
			  </span>
		    </div>
          </div><!--  control-group  -->
          <div class="control-group">
	        <p class="control-label">最大測試時間：</p>
		    <div class="controls">
		      <input type="range" id="runTimeRange" name="runTimeRange" value="1" min="1" max="60" step="1" onchange="runTime_show()">
			  <span class="offset">
	          <span id="runTimeValue">1</span> minutes
			  </span>
		    </div>
          </div><!--  control-group  -->
          <!--<div class="control-group">
	        <p class="control-label">其餘參數：<p>
		    <div class="controls">
	          <input class="btn btn-info" type="button" id="addTextTable" value="建立新表格" onclick="add_text_table()" >
		    </div>
          </div>--><!--  control-group  --> 
		  
		  <div id="findInputDiv">
		    <h4>尋找網站中可能需要的輸入參數:</h4>
			<div id="showInputs"></div>
	        <!-- not used now
            <input class="btn btn" type="button" id="addIntoTable" value="加入進參數表格" onclick="addIntoTable()" >
            -->
		  </div>
		  
	      <div id="tableDiv">
		    <h4>表格使用說明 :</h4>
			<p>在網站測試步驟中，若需要對特定項目輸入參數，請使用表格設定參數。</p>
			<p>以設定帳號登入為例: 第一欄請填入帳號欄位的input name，第二欄則填入想用來測試的帳號。</p>
			<p>若需要設定更多參數，點選"新增參數"可增加表格一行欄位</p>
			<p>對於不同區域的參數建議以不同的表格分別填寫，例如帳號密碼、字串使用不同表格區分</p>
            <select id="textTable" name="textTable" onchange="change_current_table()" ></select>	  	  
	        <span class="btn-group">    
	          <!--<input type="button" class="btn" id="addValueColmun" value="new value" onclick="add_new_row()" >-->
	          <!--<input type="button" class="btn" id="subValueColmun" value="cut value" onclick="cut_row()" >-->
	          <input type="button" class="btn" id="addNameRaw" value="新增參數" onclick="add_new_row()" >
	          <input type="button" class="btn" id="subNameRaw" value="刪除參數" onclick="cut_row()" >
		      <input type='button' class="btn" id='removeTable' value='刪除表格' onclick='remove_table()'>
		      <input type='button' class="btn" id='removeTable' value='參數變換' onclick='mutation_switch()'>
            </span>
			<input type="hidden" id="mutationAble" name="mutationAble" value="false">
			<input type="hidden" id="tableNum" name="tableNum" value="0">
			<input type="hidden" id="tmpSlipt" name="tmpSlipt" value="{tmp}">
			<input type="hidden" id="mutationSlipt" name="mutationSlipt" value="{mut}">
			<input type="hidden" id="tableValSplit" name="tableValSplit" value="{tVal}">
			<input type="hidden" id="mutationaccept" name="inputmutation" value="">
			<div id="uploadTable"></div>
		  </div><!--  tableDiv  -->

	    </div><!--  form_submit_content  -->
		
	    <!--<div class="tab-pane" id="form_upload_content">
		  <h4>上傳參數檔案:</h4>
		  <p>檔案內容請依照規定:第一行為測試目標網址，第二行為網站測試深度，第三行為最大測試時間，第四行為參數格數量</p>
		  <p>若有參數表格，在第五行開始依序寫上表格。每個表格第一行為table，接著每一行代表一行欄位row，第一項為input name，後面接input value</p>
	      <input type="file" id="uploadFile" name="uploadFile" form="upload">
	    </div>  form_upload_content  --> 
		
      </div><!--  tab-content  -->
		  
	  <div id="submit_result"></div>
      <!--  show-submit-result  -->
	  
	  <div id="check_ready"></div>
      <!--  check-ready-result  -->
		  
      <div class="form-actions">		  
	    <input class="btn btn-large btn-primary" type="button" id="submitText" value="提交" onclick="submit_text()" >
	    <input class="btn btn-large btn-primary" type="button" id="run_exec" value="開始測試" onclick="run()" >
	  </div><!--  form-actions  -->
		<input type ="hidden" id="submit_sql_id" name="submit_sql_id" value=""> 
        <input type ="hidden" id="filename" name="filename" value='tmp.txt'>
        <input type ="hidden" id="formtype" name="formtype" value='submit'>
	  </form><!--  form:page_content -->	
		
      <form id="download" name="download" method="post" action="download.php">
        <input type ="hidden" id="dirname" name="dirname" value=''>
      </form><!--  form:download  -->
      <form id="upload" name="path_content" method="post" action="uploadTxt.php" enctype="multipart/form-data">
      </form>	<!--  form:upload  -->
	
	  <hr>
	  <div class="footer">
	    <h6>@copyright by BL618</h6>
	  </div>
	
    </div><!--  container  -->
	
  </body>
</html>