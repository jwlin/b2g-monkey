<?php
session_start();
header("Content-Type:text/html; charset=utf-8");
include("mysqlInc.php");

?>
<?php 
	if($_SESSION['user_account']!=null)
    { // 如果登入過，則直接轉到登入後頁面
    	echo '<meta http-equiv=REFRESH CONTENT=0;url=record_page.php>';
    }
	else 
    {
		$user_account = $_POST['user_account'];
    	$user_password = $_POST['user_password'];
		$user_account = preg_replace("/[^A-Za-z0-9]/","",$user_account);
    	$user_password = preg_replace("/[^A-Za-z0-9]/","",$user_password);
		if($user_account!=NULL && $user_password!=NULL)
        {
	        $sql = "SELECT user_account, user_password FROM user WHERE user_account='$user_account' AND user_password='$user_password'";
	        $result = mysql_query($sql);
	        $row = mysql_fetch_array($result);
	        // 比對密碼
	        if($row['user_password']==$user_password)
            {
	            $_SESSION['user_account'] = $row['user_account'];
	            $_SESSION['user_password'] = $row['user_password'];
                
	            echo '<meta http-equiv=REFRESH CONTENT=0;url=record_page.php>';
	        }
            else
            {
	        	echo "<script>alert('Wrong account or password')</script>";
	        }
	    }
	}
?>

<html>
    <head>
    <meta charset="UTF-8">
    <link rel=stylesheet type="text/css" href="login.css">
    </head>
    <body bgcolor="#66CCBB">

        <div id="container">
            <h1>***登入***</h1>
            <form  action="login.php" method="post">
                帳號：<input type="text" name="user_account"><br/>
                密碼：<input type="password" name="user_password"><br/>
                <input type="submit"  value="登入">
                <input type="button"  onclick="location.href='register.php'" value="申請帳號" />
            </form>
            <img id="img" src="img/internet.jpg">
            </br>
            <font>NTU BL618</font>
        </div>
        
    </body>
    
</html>