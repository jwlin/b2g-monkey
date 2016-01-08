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
					$('#error_debug').append(msg['json']);
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
	for(var n = 0; n < trace_number; n++ )
	{
		var cluster = msg['traces'][n]['cluster_value'];
		if( n==0 ){
			cluster = cluster.substring(2);
			var trace_name = "測試路徑基準\t\t";
		}else{			
			var trace_name = "第"+n+"條數值變異路徑\t\t";
		}
		if( cluster == default_cluster ){
			var same_result = "<font size=\"7\" >\t通過\t</font>";
		}else{
			var same_result = "<font size=\"6\" color=\"red\">\t不通過\t</font>";
		}
		var cluster_path = cluster[0];
		for(var c = 1; c < cluster.length; c++ ){
			cluster_path += '->'+cluster[c];
		}
		var input = "<font size=\"6\">"+trace_name+cluster_path+"</font>"+same_result+
				"<input id=\""+n+"_toggle_button\" type=\"button\" value=\"顯示\" onclick=\"toggle_trace("+n+")\">"+
				"<div id=\""+n+"_mutation_trace\" style=\"display: none;\">";
		var edge_number = msg['traces'][n]['edges'].length;
		for(var i=0;i<edge_number;i++)
		{
			input += "<hr style=\"width:50%\"><font size=\"5\">第"+i+"步 : "+
					"從頁面 ID:"+msg['traces'][n]['edges'][i]['from']+
					"\t\t"+msg['traces'][n]['states'][i]['url']+
					"<br>到頁面 ID:"+msg['traces'][n]['edges'][i]['to']+					
					"\t\t"+msg['traces'][n]['states'][i+1]['url']+"<br></font>";
			input += "<font size=\"5\">點擊物件<br><table align=\"center\" border=\"1\"><tr><td>id</td><td>name</td></tr>"+
					"<tr><td>"+msg['traces'][n]['edges'][i]['clickable']['id']+"</td>"+
					"<td>"+msg['traces'][n]['edges'][i]['clickable']['name']+"</td></tr></table><br></font>";
			var inputs_number = msg['traces'][n]['edges'][i]['inputs'].length;
			input += "<font size=\"5\">輸入欄位 : </font>";
			if(inputs_number<=0){	input += "<font size=\"5\">無</font><br>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\">"+
					"<tr><td>id</td><td>name</td><td>value</td><td>變異方式</td></tr>";
				for(var input_number=0;input_number<inputs_number;input_number++){
					input += "<tr><td>"+msg['traces'][n]['edges'][i]['inputs'][input_number]['id']+"</td>"+
							"<td>"+msg['traces'][n]['edges'][i]['inputs'][input_number]['name']+"</td>"+
							"<td>"+msg['traces'][n]['edges'][i]['inputs'][input_number]['value']+"</td>"+
							"<td>"+msg['traces'][n]['edges'][i]['inputs'][input_number]['info']+"</td></tr>";
				}
				input += "</table>";
			}
			var selects_number = msg['traces'][n]['edges'][i]['selects'].length;
			input += "<font size=\"5\">下拉選單 : </font>";
			if(selects_number<=0){	input += "<font size=\"5\">無</font><br>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\">"+
					"<tr><td>id</td><td>name</td><td>selected id</td><td>selected value</td></tr>";
				for(var select_number=0;select_number<selects_number;select_number++){
					var selected_id = msg['traces'][n]['edges'][i]['selects'][select_number]['selected'];
					var values = msg['traces'][n]['edges'][i]['selects'][select_number]['value'];					
					var selected_value = ( !isNaN(selected_id) && parseInt(selected_id)<values.length )? values[parseInt(selected_id)] : 'Null';

					input += "<tr><td>"+msg['traces'][n]['edges'][i]['selects'][select_number]['id']+"</td>"+
							"<td>"+msg['traces'][n]['edges'][i]['selects'][select_number]['name']+"</td>"+
							"<td>"+selected_id+"</td><td>"+selected_value +"</td></tr>";
				}
				input += "</table>";
			}
			var radios_number = msg['traces'][n]['edges'][i]['radios'].length;
			input += "<font size=\"5\">單選按鈕: </font>";
			if(radios_number<=0){	input += "<font size=\"5\">無</font><br>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\">"+
					"<tr><td>name</td><td>selected</td><td>value</td></tr>";
				for(var radio_number=0;radio_number<radios_number;radio_number++){
					var selected = msg['traces'][n]['edges'][i]['radios'][radio_number]['radio_selected'];
					var radio_list = msg['traces'][n]['edges'][i]['radios'][radio_number]['radio_list'];
					var value = ( !isNaN(selected) && parseInt(selected)<radio_list.length )? radio_list[parseInt(selected)]['value'] : 'Null';
					input += "<tr><td>"+msg['traces'][n]['edges'][i]['radios'][radio_number]['radio_name']+"</td>"+
							"<td>"+selected+"</td><td>"+value+"</td></tr>";
				}
				input += "</table>";
			}
			var checkboxes_number = msg['traces'][n]['edges'][i]['checkboxes'].length;
			input += "<font size=\"5\">複選按鈕 : </font>";
			if(checkboxes_number<=0){	input += "<font size=\"5\">無</font>"; }
			else{
				input += "<br><table align=\"center\" border=\"1\">"+
					"<tr><td>name</td><td>selected list</td><td>value list</td></tr>";
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
				input += "</table>";
			}
			
		}
		input += "</div><hr/>";
		$("#mutation_result_container").append(input);
	}
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
