$(document).ready(function(){
	read_mutation()
	timer = setInterval("read_mutation()", 10000);
})
function read_mutation()
{	
	$.ajax({
		url:"check_mutation_trace.php",
		data:{
			dirname:$("#hidden_dirname").val(),
			trace_number:$("#hidden_trace_number").val()
		},
		type:"POST",
		datatype:"json",
		success: function(js)
		{
          	var msg = jQuery.parseJSON(js);
          	if(msg['end'])
          	{
          		clearInterval(timer);
          		if(msg['complete']){
          			$("#marquee").hide();
          			show_mutation(msg['json']);
          		}
          		else{
          			$("#marquee").text("ERROR 很抱歉程式發生錯誤，請靜待工程師修復問題");
					$('#error_debug').append( $("<pre style='text-align: left;'></pre>").text( msg['json']) );
					$('#error_debug').append( "<br>" );
          		}
          	}			
		},
        error: function(js){
          	alert('err');
        },
        beforeSend: function(){
        }
	});
}
function show_mutation(msg)
{
	var methodLabel = ["全部欄位變異","","個別欄位變異", ""];
	var modeLable = ["Empty","Max Length","Random String","Malformed Symbol","SQL Injection"]
	// correct the title
	$('#method').text(methodLabel[ msg['method']-1 ]);
	$('#mode').text(modeLable[ msg['mode']-1 ]);

	$("#mutation_result_container").removeClass("disable");
	var trace_number = msg['traces'].length;
	// default trace cluster
	var default_cluster = msg['traces'][0]['cluster_value'].substring(2);
	var n = 0, trace_number = msg['traces'].length;
	for(; n < trace_number; n++ )
	{
		if( n==0 ){
			var trace_name = "測試路徑的基準\t\t";
			var same_result = "";
		}else{			
			var trace_name = "第"+n+"條數值變異路徑\t\t";
			var same_result = (msg['traces'][n]['cluster_value'] == default_cluster) ? 
				"<font size=\"6\" >\t通過\t</font>" : "<font size=\"6\" color=\"red\">\t不通過\t</font>";
		}
		var input = "<font size=\"6\">"+trace_name+"</font>"+same_result+
				"<input id=\""+n+"_toggle_button\" type=\"button\" class=\"show_button\" value=\"顯示\" onclick=\"toggle_trace("+n+")\">"+
				"<div id=\""+n+"_mutation_trace\" style=\"display: none;\">"+
				"<table align=\"center\" border=\"1\" >";
		var i=0, edge_number = msg['traces'][n]['edges'].length;
		for( ;i < edge_number; i++)
		{
			input += "<tr><td>";
			input += "<font size=\"5\"><div style=\"text-align: center;\"><br>第"+(i+1)+"個頁面</div><hr>"+
					"網頁編號:"+msg['traces'][n]['states'][i]['id']+"<br>"+
					"網址:"+msg['traces'][n]['states'][i]['url']+"<br><br></font>";
			input += "<font size=\"5\">點擊物件 : <br></font>"+
					"<table align=\"center\" border=\"1\" cellpadding=\"5\">"+
					"<tr><th>id(html元件名稱)</th><th>name(html元件名稱)</th><th>xpath(html元件名稱)</th></tr>"+
					"<tr><td>"+msg['traces'][n]['edges'][i]['clickable']['id']+"</td>"+
					"<td>"+msg['traces'][n]['edges'][i]['clickable']['name']+"</td>"+
					"<td>"+msg['traces'][n]['edges'][i]['clickable']['xpath']+"</td></tr></table><br>";

			var inputs_number = msg['traces'][n]['edges'][i]['inputs'].length;
			input += "<font size=\"5\">輸入欄位 input : </font>";
			if(inputs_number<=0){	input += "<font size=\"5\">無</font><br>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\" cellpadding=\"5\">"+
					"<tr><th>id(html元件名稱)</th><th>name(html元件名稱)</th><th>value(html元件名稱)</th><th>變異方式</th></tr>";
				for(var input_number=0;input_number<inputs_number;input_number++){
					var mutation_info = msg['traces'][n]['edges'][i]['inputs'][input_number]['info'] ?
						msg['traces'][n]['edges'][i]['inputs'][input_number]['info'] : "無變異";
					var value = replaceToLegal(msg['traces'][n]['edges'][i]['inputs'][input_number]['value']);
					input += "<tr><td>"+msg['traces'][n]['edges'][i]['inputs'][input_number]['id']+"</td>"+
							"<td>"+msg['traces'][n]['edges'][i]['inputs'][input_number]['name']+"</td>"+
							"<td>"+value+"</td>"+
							"<td>"+mutation_info+"</td></tr>";
				}
				input += "</table><br>";
			}

			var selects_number = msg['traces'][n]['edges'][i]['selects'].length;
			input += "<font size=\"5\">下拉選單 select : </font>";
			if(selects_number<=0){	input += "<font size=\"5\">無</font><br>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\" cellpadding=\"5\">"+
					"<th>id(html元件名稱)</th><th>name(html元件名稱)</th><th>選擇第幾個option</th><th>value(html元件名稱)</th></tr>";
				for(var select_number=0;select_number<selects_number;select_number++){
					var selected_id = msg['traces'][n]['edges'][i]['selects'][select_number]['selected'];
					var values = msg['traces'][n]['edges'][i]['selects'][select_number]['value'];					
					var selected_value = ( !isNaN(selected_id) && parseInt(selected_id)<values.length )? values[parseInt(selected_id)] : 'Null';

					input += "<tr><td>"+msg['traces'][n]['edges'][i]['selects'][select_number]['id']+"</td>"+
							"<td>"+msg['traces'][n]['edges'][i]['selects'][select_number]['name']+"</td>"+
							"<td>"+selected_id+"</td><td>"+selected_value +"</td></tr>";
				}
				input += "</table><br>";
			}

			var radios_number = msg['traces'][n]['edges'][i]['radios'].length;
			input += "<font size=\"5\">單選按鈕 radio : </font>";
			if(radios_number<=0){	input += "<font size=\"5\">無</font><br>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\" cellpadding=\"5\">"+
					"<tr><th>name(html元件名稱)</th><th>選擇第幾個radio</th><th>value(html元件名稱)</th></tr>";
				for(var radio_number=0;radio_number<radios_number;radio_number++){
					var selected = msg['traces'][n]['edges'][i]['radios'][radio_number]['radio_selected'];
					var radio_list = msg['traces'][n]['edges'][i]['radios'][radio_number]['radio_list'];
					var value = ( !isNaN(selected) && parseInt(selected)<radio_list.length )? radio_list[parseInt(selected)]['value'] : 'Null';
					input += "<tr><td>"+msg['traces'][n]['edges'][i]['radios'][radio_number]['radio_name']+"</td>"+
							"<td>"+selected+"</td><td>"+value+"</td></tr>";
				}
				input += "</table><br>";
			}

			var checkboxes_number = msg['traces'][n]['edges'][i]['checkboxes'].length;
			input += "<font size=\"5\">複選按鈕 checkbox : </font>";
			if(checkboxes_number<=0){	input += "<font size=\"5\">無</font>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\" cellpadding=\"5\">"+
					"<tr><th>name(html元件名稱)</th><th>選擇哪幾個checkbox</th><th>value(html元件名稱)</th></tr>";
				for(var checkbox_number=0;checkbox_number<checkboxes_number;checkbox_number++){
					var checkbox_list = msg['traces'][n]['edges'][i]['checkboxes'][checkbox_number]['checkbox_list'];
					var checkbox_selected_list = msg['traces'][n]['edges'][i]['checkboxes'][checkbox_number]['checkbox_selected_list'];
					var checkbox_value_list = [];
					for(var v = 0; v < checkbox_selected_list.length && v < checkbox_list.length; v++ ){
						var selected = checkbox_selected_list[v]
						if ( !isNaN(selected) && parseInt(selected)<checkbox_list.length ){
							checkbox_value_list.push( checkbox_list[parseInt(selected)]['value'] );
						}else{
							checkbox_value_list.push('Null');
						}
					}
					input += "<tr><td>"+msg['traces'][n]['edges'][i]['checkboxes'][checkbox_number]['checkbox_name']+"</td>"+
							"<td>"+checkbox_selected_list+"</td><td>"+checkbox_value_list+"</td></tr>";
				}
				input += "</table><br>";
			}
			input += "</td>";
			src = "../python/trace/"+$('#hidden_dirname').val()+"/mutant/mutant"+$("#hidden_trace_number").val()+"/"+
				msg["traces"][n]["states"][i]["img_path"];
			input += "<td><a href=\""+src+"\" target=\"_blank\"><img class=\"img\" src=\""+src+"\"/></a><br/></font>"+
					"</td></tr>";		
		}
		input += "<tr><td>";
		input += "<font size=\"5\"><div style=\"text-align: center;\"><br>第"+(i+1)+"個頁面</div><hr>"+
				"網頁編號:"+msg['traces'][n]['states'][i]['id']+"<br>"+
				"網址:"+msg['traces'][n]['states'][i]['url']+"<br></font>";
		input += "</td>";
		src = "../python/trace/"+$('#hidden_dirname').val()+"/mutant/mutant"+$("#hidden_trace_number").val()+"/"+
			msg["traces"][n]["states"][i]["img_path"];
		input += "<td><a href=\""+src+"\" target=\"_blank\"><img class=\"img\" src=\""+src+"\"/></a><br/></font>"+
				"</td></tr>";
		input += "</table></div><hr>";
		$("#mutation_result_container").append(input);
	}
}

function replaceToLegal(str){
	return str.replace(/&/g, "&amp;").replace(/</g, "&alt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;").replace(/-/g, "&ndash;");
}

function toggle_trace(n){
	div_id = "#"+n+"_mutation_trace";
	button_id= "#"+n+"_toggle_button";
	$(div_id).toggle();
	if( $(button_id).val() == '顯示'){
		$(button_id).val('隱藏');
	}else{
		$(button_id).val('顯示');

	}
}
