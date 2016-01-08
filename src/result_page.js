$(document).ready(function(){   
	check_trace_exist();
	timer = setInterval("check_trace_exist()", 10000);
})

function new_task()
{
	window.open("start.php");
}
function old_result(){
	$('h1').append('.');
	$.ajax({
		url:"redirect_result_page.php",
		data:{
			dirname: $('#old_dirname').val()
		},
		type:"POST",
		datatype:"json",
		success: function(ms){
          	var msg = jQuery.parseJSON(ms);
			if(msg['exist'] && msg['complete']){	
				window.location.href = "result_page.php";
			}
			else{
				alert(ms+'this dir not exist or complete!')
			}
		},
        error: function(check_value){
          	alert('err redirect');
        }
	});
}

function check_trace_exist(){
	$.ajax({
		url:"check_trace.php",
		data:{dirname:$("#hidden_dirname").val()},
		type:"POST",
		datatype:"json",
		success: function(check_value){
          	var msg = jQuery.parseJSON(check_value);
			//console.log(JSON.stringify(msg));
			if(msg['end'])
			{				
				clearInterval(timer);
          		if(msg['complete'])
          		{
					$("#marquee").addClass("disable");
					read_trace(msg["json"]);
          		}
          		else
          		{
					$('#error_debug').append(msg['json']);
          		}
			}
		},
        error: function(check_value)
        {
          	alert('err check trace');
        }
	});

}
function read_trace(msg)
{
			$("#state_information").removeClass("disable");
			$("#iframe").removeClass("disable");
			var number = msg["traces"].length;
			var i = 0;
			for(i = 0;i<number;i++)
			{
				var tr_num = document.getElementById("state_information").rows.length;
				var tr = document.getElementById("state_information").insertRow(tr_num);
				
				var td = tr.insertCell(tr.cells.length);
				var state_number = msg["traces"][i]["states"].length;
				//td.innerHTML = "<p> Trace{0}, init:{1}, end{2}, length{3}<\p>".format(i, msg["traces"][i]["states"][0]["id"], msg["traces"][i]["states"][state_number-1]["id"],state_number);
				td.innerHTML = "<font > 第"+i+"路徑： 從起點 "+msg["traces"][i]["states"][0]["id"]+" 到終點 "+msg["traces"][i]["states"][state_number-1]["id"]+" ,路徑長度 "+state_number+" </font>";
				var td = tr.insertCell(tr.cells.length);

				td.innerHTML = "<input type=\"button\" value=\"查看細節\" id=\""+i+"_detail\" onclick=\"see_detail("+i+","+number+")\">";
				var td = tr.insertCell(tr.cells.length);
				td.innerHTML = "<input type=\"button\" value=\"產生Jmeter檔案\" id=\""+i+"\" onclick=\"create_jmeter("+i+")\">";
				
				var td = tr.insertCell(tr.cells.length);
				td.innerHTML = "<form action=\"download.php\" method=\"POST\">"+
					"<input type=\"submit\" value=\"下載\" class=\"download_disable download_class\" id=\""+i+"_download\">"+
					"<input name=\"filename\" type=\"hidden\" value=\""+$("#hidden_dirname").val()+"/jmeter/jmeter"+i+".jmx\"></form> ";
				$("#download_container").append('<div id="detail_'+i+'" class="detail detail_none"> </div>');
				write_detail(i,msg);

				var td = tr.insertCell(tr.cells.length);
				td.innerHTML = "<input type=\"button\" value=\"數值變異測試\" id=\""+i+"\" onclick=\"check_mutation_status("+i+")\">"+
					"<input type=\"button\" value=\"清空\" id=\"clean"+i+"\" onclick=\"clean_mutation("+i+")\" >";
			}
}

function run_mutation(id)
{
	$.ajax({
		url:"runAjax_mutation.php",
		data:{
			dirname:$("#hidden_dirname").val(),
			trace_number:id,
			method:$("#mutaton_select option:selected").val(),
			mode: $("#mutaton_mode option:selected").val(),
			max:$("#mutation_max").val()
		},								
		type:"POST",
		datatype:"json",
		success: function(js)
		{
			var msg = jQuery.parseJSON(js); 
			alert('cmd:'+msg['cmd']+"\nrun:"+msg['run']);
			setTimeout(function(){
				$("#send_id_to_mutation").submit();
			}, 1000);
		},
        error: function(js){
		  	var msg = jQuery.parseJSON(js); 
			alert('ERROR\ncmd:'+msg['cmd']+"\nrun:"+msg['run']);
        }

	});
}

function check_mutation_status(id){
	$("#send_select_id").val($("#mutaton_select option:selected").val());
	$("#send_select_mode").val($("#mutaton_mode option:selected").val());
	$("#send_select_id_text").val($("#mutaton_select option:selected").text());
	$("#send_select_mode_text").val($("#mutaton_mode option:selected").text());
	$("#send_trace_number").val(id);
	$("#send_dirname").val($("#hidden_dirname").val());

	$.ajax({
		url:"check_mutation_trace.php",
		data:{
			dirname:$("#hidden_dirname").val(),
			trace_number:id
		},
		type:"POST",
		datatype:"json",
		success: function(js)
		{
          	var msg = jQuery.parseJSON(js);
          	alert(js);
          	if( !msg['exist'] ){
          		run_mutation(id);
          	}else{
				setTimeout(function(){
					$("#send_id_to_mutation").submit();
				}, 1000);
          	}
		},
        error: function(js){
          	alert(js);
        }
	});
}

function clean_mutation(id){
	$.ajax({
		url:"delete.php",
		data:{
			dirname:"/var/www/python/trace/"+$("#hidden_dirname").val()+"/mutant/mutant"+id,
		},
		type:"POST",
		datatype:"txt",
		success: function(js){
			alert(js);
		},
        error: function(js){
          	alert('err');
        }
	});
}

function see_detail(id,number)
{	
	var n;
	for(n=0;n<number;n++)
	{
		var j = "#detail_"+n+"";
		$(j).addClass("detail_none");
	}
	var i = "#detail_"+id+"";
	$(i).removeClass("detail_none");


}
function write_detail(number,msg)
{
	var i = "#detail_"+number+"";
	var state_number = msg["traces"][number]["states"].length;
	var n;
	for(n=0;n<state_number-1;n++)
	{
		input = "<font size=\"5\">第"+n+"個頁面  網頁編號:"+msg["traces"][number]["states"][n]["id"]+"  網址:"+msg["traces"][number]["states"][n]["url"]+"<br></font>";
		$(i).append(input);
		src = "../python/trace/"+$('#hidden_dirname').val()+"/"+msg["traces"][number]["states"][n]["img_path"];
		input = "<a href=\""+src+"\" target=\"_blank\"><img class=\"img\" src=\""+src+"\"/></a><br/></font>";
		$(i).append(input);
		input = "<hr/><font size=\"5\">點擊物件<br>"+
				"<table align=\"center\" border=\"1\" ><tr><td> id </td><td> name </td><td> xpath </td></tr>"+
				"<tr><td>"+msg["traces"][number]["edges"][n]["clickable"]["id"]+"</td>"+
				"<td>"+msg["traces"][number]["edges"][n]["clickable"]["name"]+"</td>"+
				"<td>"+msg["traces"][number]["edges"][n]["clickable"]["xpath"]+"</td></tr></table><br><hr/></font>";
		$(i).append(input);

	}
	input = "<font size=\"5\">第"+n+"個頁面  網頁編號:"+msg["traces"][number]["states"][n]["id"]+"  網址:"+msg["traces"][number]["states"][n]["url"]+" <br></font>";
	$(i).append(input);
	src = "../python/trace/"+$('#hidden_dirname').val()+"/"+msg["traces"][number]["states"][n]["img_path"];
	input = "<a href=\""+src+"\" target=\"_blank\"><img class=\"img\" src=\""+src+"\"/></a><br/></font>";
	$(i).append(input);

	input = "<input type=\"button\" value=\"關閉\" onclick=\"remove_all("+number+")\">";
	$(i).append(input);
}
function remove_all(number)
{
	var i = "#detail_"+number+"";
	$(i).addClass("detail_none");
}
function create_jmeter(id)
{
	var i = "#"+id+"_download";
	$.ajax({
		url:"create_jmeter.php",
		data:{dirname:$("#hidden_dirname").val(),
			  trace_number:id},								
		type:"POST",
		datatype:"json",
		success: function(js)
		{
			var msg = jQuery.parseJSON(js); 
			alert('OUT:'+msg['out']+'\nERROR:'+msg['er']);
			$(i).removeClass("download_disable");
		},
        error: function(js)
        {
		  	var msg = jQuery.parseJSON(js); 
        }

	});

}