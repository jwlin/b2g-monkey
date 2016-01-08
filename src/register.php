<?php 
	
	session_start();
	include("mysqlInc.php"); 
	
	function getIP()
    {
		$ip = "";
	    if (!empty($_SERVER['HTTP_CLIENT_IP'])){
	        $ip = $_SERVER['HTTP_CLIENT_IP'];
	    }
	    else if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])){
	        $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
	    }
	    else {
	        $ip = $_SERVER['REMOTE_ADDR'];
	    }
	    return $ip;
	}
	
	
	if($_POST['user_account'] && $_POST['user_password']  )
    {
		
	  
	    $user_account = mysql_real_escape_string($_POST['user_account']);
		$user_password = mysql_real_escape_string($_POST['user_password']);
		$ip = getIp();
		/*驗證帳號重複*/
		$sql = "SELECT user_account FROM user WHERE user_account='$user_account'";
		if(mysql_num_rows(mysql_query($sql))!=0)
			echo "<script>alert('This account was registered!')</script>";
		else
        {
			/*創建*/
		    $sql = "INSERT INTO user (user_account, user_password, working) VALUES ('$user_account','$user_password', 0)";
		    mysql_query($sql);
			echo '<meta http-equiv=REFRESH CONTENT=0;url=login.php>';
		}
	}
?>

<!DOCTYPE html>
<html >
	<head>
		<meta charset="utf-8">
		<link rel=stylesheet type="text/css" href="register.css">
		<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
		
	</head>
	
	<body bgcolor="ffffcc">
		
			<input type="button" id="return" onclick="location.href='login.php'" value="回到登入頁面" />
			
			<div id="container">
				<h1>***註冊***</h1>
				<form action="register.php" method="post">
					帳號：<input type="text" name="user_account"><br/>
					</br>
                    密碼：<input type="password" name="user_password"><br/>
					
                  	<input type="submit"  value="送出" />

				</form>	
				</br>		
			 	<img id="img" src="img/internet.jpg">
            	</br>

            	<font>NTU BL618</font>
        	</div>
		
	</body>
</html>