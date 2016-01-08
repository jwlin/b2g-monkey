function check_record(user_dirname)
{
	$("#choose").val(user_dirname);
	old_result();
}
function old_result()
{
	$.ajax({
		url:"redirect_result_page.php",
		data:{
			dirname: $("#choose").val()
		},
		type:"POST",
		datatype:"json",
		success: function(ms)
		{
          	var msg = jQuery.parseJSON(ms);
			if(msg['exist'])
			{		
				window.location.href = "result_page.php";
			}
			else{
				alert(ms+'this dir not exist')
			}
		},
        error: function(check_value)
        {
          	alert('err redirect');
        }
	});
	
}