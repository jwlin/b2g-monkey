$(document).ready(function(){   
	check_trace_exist();
	timer = setInterval("check_trace_exist()", 10000);
})

function check_trace_exist(){
	$.ajax({
		url:"check_trace.php",
		data:{dirname:$("#hidden_dirname").val()},
		type:"POST",
		datatype:"json",
		success: function(check_value){
          	var msg = jQuery.parseJSON(check_value);
			if(msg['end'])
			{				
				clearInterval(timer);
          		if(msg['complete']){
					$("#marquee").addClass("disable");
					read_trace(msg["json"], msg["mutant"]);
          		}
          		else{
          			$("#marquee").text("ERROR 很抱歉程式發生錯誤，請靜待工程師修復問題");
					$('#error_debug').append( $("<pre style='text-align: left;'></pre>").text( msg['json']) );
					$('#error_debug').append( "<br>" );
          		}
			}
		},
        error: function(check_value)
        {
          	alert('err check trace');
        }
	});

}

//=================================================================
//=================================================================
function read_trace(msg, msg_mutant)
{
	$("#state_information").removeClass("disable");
	$("#iframe").removeClass("disable");

	$("#state_information").append()


	var number = msg["traces"].length;
	for(var i = 0;i<number;i++)
	{
		var tr_num = document.getElementById("state_information").rows.length;
		var tr = document.getElementById("state_information").insertRow(tr_num);
		var inputs_num = 0;
		for(var n = 0; n < msg["traces"][i]["edges"].length; n++ ){
			inputs_num += msg["traces"][i]["edges"][n]["inputs"].length;
		}
		if( inputs_num == 0 ){
			console.log(i+" 0 inputs");
			tr.classList.add("noInput");
		}
		
		var td = tr.insertCell(tr.cells.length);
		var state_number = msg["traces"][i]["states"].length;
		//td.innerHTML = "<p> Trace{0}, init:{1}, end{2}, length{3}<\p>".format(i, msg["traces"][i]["states"][0]["id"], msg["traces"][i]["states"][state_number-1]["id"],state_number);
		td.innerHTML = "<font > 第"+(i+1)+"個路徑： 從起點 "+msg["traces"][i]["states"][0]["id"]+
			" 到終點 "+msg["traces"][i]["states"][state_number-1]["id"]+
			" ,路徑長度 "+state_number+" </font>"+
			"<input type=\"button\" value=\"查看細節\" id=\""+i+"_detail\" onclick=\"see_detail("+i+","+number+")\">";

		var td = tr.insertCell(tr.cells.length);
		var jmeter_button = "<input type=\"button\" value=\"下載Jmeter檔案\" onclick=\"download_jmeter("+i+")\" >"+
			"<input type=\"button\" value=\"傳送Jmeter檔案至測試平台開始測試\" onclick=\"sendfile_jmeter("+i+")\" >";
		td.innerHTML = jmeter_button;

		$("#download_container").append('<div id="detail_'+i+'" class="detail detail_none"> </div>');
		write_detail(i,msg);

		var td = tr.insertCell(tr.cells.length);
		var mutant = "/var/www/python/trace/"+$("#hidden_dirname").val()+"/mutant/mutant"+i;		
		var mutation_button = ( jQuery.inArray(mutant, msg_mutant) >= 0 ) ? 
			"<input type=\"button\" value=\"開始變異測試\" id=\"new"+i+"\" onclick=\"start_mutation("+i+",true)\">"+
			"<input type=\"button\" value=\"檢視測試結果\" id=\"look"+i+"\" onclick=\"look_mutation("+i+")\" >" : 
			"<input type=\"button\" value=\"開始變異測試\" id=\"new"+i+"\" onclick=\"start_mutation("+i+",false)\">"+
			"<input type=\"button\" value=\"檢視測試結果\" disabled=\"disabled\"  id=\"look"+i+"\" onclick=\"look_mutation("+i+")\" >";
		td.innerHTML = mutation_button;
	}
}

//=================================================================
//=================================================================
function write_detail(number,msg){
	var i = "#detail_"+number+"";
	var state_number = msg["traces"][number]["edges"].length;
	var n=0;
	input="<table class=\"information\" align=\"center\" border=\"1\" >";
	for(;n<state_number;n++)
	{
		input += "<tr><td>"+
				"<font size=\"5\"><div style=\"text-align: center;\"><br>第"+(n+1)+"個頁面</div><hr>"+
				"網頁編號:"+msg["traces"][number]["states"][n]["id"]+"<br>"+
				"網址:"+msg["traces"][number]["states"][n]["url"]+"<br><br></font>"+
				"<font size=\"5\">點擊物件<br></font>";
		input += "<table align=\"center\" border=\"1\" ><tr><th> id(html元件名稱) </th><th> name(html元件名稱) </th><th> xpath(html元件名稱) </th></tr>"+
				"<tr><td>"+msg["traces"][number]["edges"][n]["clickable"]["id"]+"</td>"+
				"<td>"+msg["traces"][number]["edges"][n]["clickable"]["name"]+"</td>"+
				"<td>"+msg["traces"][number]["edges"][n]["clickable"]["xpath"]+"</td></tr></table><br>"+
				"</td>";
		src = "../python/trace/"+$('#hidden_dirname').val()+"/"+msg["traces"][number]["states"][n]["img_path"];
		input += "<td><a href=\""+src+"\" target=\"_blank\"><img class=\"img\" src=\""+src+"\"/></a><br/></font>"+
				"</td></tr>";
	}
	input += "<tr><td>"+
			"<font size=\"5\"><div style=\"text-align: center;\"><br>第"+(n+1)+"個頁面</div><hr>"+
			"網頁編號:"+msg["traces"][number]["states"][n]["id"]+"<br>"+
			"網址:"+msg["traces"][number]["states"][n]["url"]+"<br><br></font>"+
			"</td><td>";
		
	src = "../python/trace/"+$('#hidden_dirname').val()+"/"+msg["traces"][number]["states"][n]["img_path"];
	input += "<a href=\""+src+"\" target=\"_blank\"><img class=\"img\" src=\""+src+"\"/></a><br/></font>"+
			"</td></tr>"+"</table>";
	$(i).append(input);

	input = "<input type=\"button\" class=\"show_button\" value=\"關閉\" onclick=\"remove_all("+number+")\">";
	$(i).append(input);
}
function see_detail(id,number){	
	var n;
	for(n=0;n<number;n++){
		var j = "#detail_"+n+"";
		$(j).addClass("detail_none");
	}
	var i = "#detail_"+id+"";
	$(i).removeClass("detail_none");
}
function remove_all(number){
	var i = "#detail_"+number+"";
	$(i).addClass("detail_none");
}

//=================================================================
//=================================================================
function showAllTrace(){
	$("#state_information tr").show();
}
function HideNoInputTrace(){
	$("#state_information tr.noInput").hide();
	$(".detail").addClass("detail_none");
}

//=================================================================
//=================================================================
function download_jmeter(id){
	var filename = $("#hidden_dirname").val()+'/jmeter/jmeter'+id+".jmx";
	$("#download_filename").val(filename);
	create_jmeter(id, "#download_form");
}
function sendfile_jmeter(id){
	var filename = $("#hidden_dirname").val()+'/jmeter/jmeter'+id+".jmx";
	var timedir = $("#hidden_dirname").val().replace(/:/g,"_");
	var fname = "jmeter"+id+".jmx";
	$("#sendfile_filename").val(filename);
	$("#sendfile_timedir").val(timedir);
	$("#sendfile_fname").val(fname);
	create_jmeter(id, "#sendfile_form");
}
function create_jmeter(id, form){
	$.ajax({
		url:"create_jmeter.php",
		data:{dirname:$("#hidden_dirname").val(),
			  trace_number:id},								
		type:"POST",
		datatype:"json",
		success: function(js){
			var msg = jQuery.parseJSON(js);
			if(msg["er"]){
				alert('ERROR:'+msg['er']);
				console.log(msg['out'].join('\n'));	
			}
			else{
				console.log(msg['out']);
				$(form).submit();	
			}
		},
        error: function(js){
        	alert("Error to make jmeter file");
        }
	});
}


//=================================================================
//=================================================================
function start_mutation(id, done_before){
	$("#send_select_id").val($("#mutaton_select option:selected").val());
	$("#send_select_id_text").val($("#mutaton_select option:selected").text());
	$("#send_trace_number").val(id);
	$("#send_dirname").val($("#hidden_dirname").val());

	if(done_before){ replay_mutation(id); }
	else{	run_mutation(id); }
}
function run_mutation(id){
	$("#look"+id).prop('disabled', false);
	console.log('max:'+$("#mutation_max").val());

	$.ajax({
		url:"runAjax_mutation.php",
		data:{
			dirname:$("#hidden_dirname").val(),
			trace_number:id,
			method:$("#mutaton_select option:selected").val(),
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
function replay_mutation(id){
	$.ajax({
		url:"delete.php",
		data:{
			dirname:"/var/www/python/trace/"+$("#hidden_dirname").val()+"/mutant/mutant"+id,
		},
		type:"POST",
		datatype:"txt",
		success: function(js){
			console.log(js);
          	run_mutation(id);
		},
        error: function(js){
          	alert('err delete last file');
        }
	});
}
function look_mutation(id){
	$("#send_select_id").val($("#mutaton_select option:selected").val());
	$("#send_select_mode").val($("#mutaton_mode option:selected").val());
	$("#send_select_id_text").val($("#mutaton_select option:selected").text());
	$("#send_select_mode_text").val($("#mutaton_mode option:selected").text());
	$("#send_trace_number").val(id);
	$("#send_dirname").val($("#hidden_dirname").val());
	$("#send_id_to_mutation").submit();
}