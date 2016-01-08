 
	var temp=Array();    
        
	$(document).ready(function(){	
      $("#findInputDiv").hide();    
	  $("#tableDiv").hide();
	  $('#findInput').addClass('disabled');
      $('#findInput').prop('disabled', true);
	  $('#run_exec').addClass('disabled');
      $('#run_exec').prop('disabled', true);
	  $('#check_running').addClass('disabled');
      $('#check_running').prop('disabled', true);
	  $('#downloadzip').addClass('disabled');
      $('#downloadzip').prop('disabled', true);
        
      $('#page_content').submit(function(){
        temp=Array(); 
        $('[name="multiSelect[]"]').each(function(){
            temp.push( $(this).val() );
        })
        $("[name='inputmutation']").val( JSON.stringify(temp) );
        
        $(this).ajaxSubmit({
            error: function(ms){
              alert('error');
            },
            success: function(ms){
              var msg = jQuery.parseJSON(ms);
              var id = msg['submit_sql_id'];
              $('#submit_sql_id').val(id);

              //TODO button abled
		      $('#run_exec').removeClass('disabled');
              $('#run_exec').prop('disabled', false);
            },
            beforeSend: function(){
            }
        });
        return false;    
      });
	  
	});
     	 	
    function range_show(){
	    $("#rangeValue").html( $("#depthRange").val() );
    }
	
	function runTime_show(){
	    $("#runTimeValue").html( $("#runTimeRange").val() );
    }
	
	var runMode = 1;
	
    var tableHistoryNum = 0;
	var tableArr = new Array();
    var tableNow = 0;
	var mutation = true;
	var mutationNum = 9;
	var mutationBlock = '<td>'
                      + '<select class = "mutantChoice" name="multiSelect[]" multiple="multiple">'
                      +	'<option value="0" >None</option>'
	                  + '<option value="1">Empty</option>'
					  + '<option value="2">Max Length</option>'
					  + '<optgroup label="Random">'
					  + '<option value="3">Random English</option>'
					  + '<option value="4">Random English(2case)</option>'
					  + '<option value="5">Random Number</option>'
					  + '<option value="6">Random negative number</option>'
					  + '<option value="7">Random English + Number</option>'
					  + '</optgroup>'
					  + '<optgroup label="Limit Number">'
					  + '<option value="8">Max Integer</option>'
					  + '<option value="9">Over Max Integer</option>'
					  + '<option value="10">Max Unsigned Integer</option>'
					  + '<option value="11">Over Max Unsigned Integer</option>'
					  + '<option value="12">Max Short Integer</option>'
					  + '<option value="13">Over Max Short Integer</option>'
					  + '<option value="14">Min Short Integer</option>'
					  + '<option value="15">Over min Short Integer</option>'
					  + '<option value="16">Min Integer</option>'
					  + '<option value="17">Over Min Integer</option>'
					  + '<option value="18">Zero</option>'
					  + '<option value="19">One</option>'
					  + '<option value="20">minus One</option>'
					  + '<option value="21">0.0000001</option>'
					  + '</optgroup>'
					  + '<optgroup label="SQL injection">'
					  + '<option value="22">"or 1=1</option>'
					  + '<option value="23">"or "x"="x</option>'
					  + '<option value="24">x" AND email IS NULL; --</option>'
					  + '</optgroup>'
					  + '<optgroup label="Malformed Symbol">'
					  + '<option value="25">&lt;&gt;</option>'
					  + '<option value="26">&lt;!---&gt;</option>'
					  + '<option value="27">//</option>'
					  + '<option value="28">/**/</option>'
					  + '<option value="29">&amp;&amp;</option>'
					  + '<option value="30">&quot;</option>'
					  + '<option value="31">&lsquo;</option>'
					  + '<option value="32">&ldquo;</option>'
					  + '<option value="33">&permil;</option>'
					  + '<option value="34">&nbsp;</option>'
					  + '</optgroup>'
					  + '<optgroup label="text Form">'
					  + '<option value="35">Web Mail Form</option>'
					  + '<option value="36">Web Address Form</option>'
					  + '<option value="37">telephone Form</option>'
					  + '<option value="38">Address Form</option>'
					  + '<option value="39">Date Form</option>'
					  + '<option value="40">Money Form</option>'
					  + '</optgroup>'
					  + '</select></td>';
	var typeBlock = '<td>'
	              + '<select onchange = "" name="inputtype[]">'
				  + '<option value = "0" selected> normal </option>'
				  + '<option value = "1" > username </option>'
				  + '<option value = "2" > password </option>'
				  + '<option value = "3" > email </option>'
				  + '<option value = "4" > url </option>'
				  + '<option value = "5" > tel </option>'
				  + '<option value = "6" > search </option>'
				  + '<option value = "7" > number </option>'
				  + '</select>'
	              + '</td>';
	var typeRow = '<tr> <td>Input name</td> <td>Input value</td> <td>Input Type</td> <td>Mutation Control</td> </tr>';
	var basicRow = '<tr><td><input type="text" name="inputname[]"></td><td><input type="text" name="inputvalue[]"></td>' + typeBlock + mutationBlock + '</br>';
				   
	function add_text_table(){
	
      if( tableArr.length == 0 ){ $("#tableDiv").show();}
	  tableHistoryNum += 1;
	  tableArr.push( 'table'+tableHistoryNum );
      $("#textTable").append( $("<option></option>").attr("value", tableArr.length).text('第'+tableArr.length+"表格") );
      var str = '<div id="table' + tableHistoryNum + '">'
              + '<table class="table table-bordered table-hover table-striped"><tbody>'
			  + typeRow + basicRow
	          + '</tbody></table></div>';
      $("#tableDiv").append(str);
      $("#textTable").val(tableArr.length);
      change_current_table();
	}
    
    function change_current_table(){
      tableNow = $("#textTable").val();
      $("#tableDiv > div").hide();
      $("#"+tableArr[tableNow-1] ).show();
	 // $('#tableDiv').find('table').find('.mutantChoice').attr('disabled', !mutation);
	  $('[name="multiSelect[]"]').multiselect();
    }
    
    function add_new_row(){
	  var t = $("#"+tableArr[tableNow-1]).find("table");
      var colnum = $(t).find("tr:first td").length;
	  var str = basicRow ;
	  t.append(str+'</tr>');
      change_current_table();
	} 
    
	function cut_row(){
	  var t = $("#"+tableArr[tableNow-1]).find("table");
	  if( t.find("tr").length > 2 ){
	    t.find("tr").last().remove();
	  }
      change_current_table();
	}
	
	function add_new_column(){
      var t = $("#"+tableArr[tableNow-1]).find("table");
      var str = '<td><input type=\"text\"></td>';
      t.find("tr").each( function(){
		  $(this).append(str);
	  });
      change_current_table();
	}	
	
	function cut_column(){
	  var t = $("#"+tableArr[tableNow-1]).find("table");
      if( t.find("tr").first().find("td").length > 2 ){
	    t.find("tr").each(function(){
		  $(this).find("td").last().remove();
		});
	  }	  
      change_current_table();
	}
	
	function remove_table(){
	  $("#"+tableArr[tableNow-1] ).remove();
	  $("#textTable").find("option").last().remove();
	  tableArr.splice(tableNow-1, 1);	  
      change_current_table();
      if( tableArr.length == 0 ){ $("#tableDiv").hide();}
	}		
	
	function undo(i){
	  i.style.display = "none";
	}
		
	function mutation_switch(){
	  $('#tableDiv').find('table').find('.mutantChoice').attr('disabled', mutation);
	  mutation = !mutation;
	  $('#mutationAble').val( mutation );
	  if(!mutation){
	    $('#tableDiv').find('table').find('select').val(0);
	    $('.mutationList').find('input').hide();
	  }
	}
	
	function table_data_serialize(){
      $("#uploadTable").html("");
	  var tmpSlipt = "{tmp}";
	  var mutationSplit = "{mut}";
      var tableValSplit = "{tVal}";
	  $("#tableNum").val(tableArr.length);
	  if( check_form() ){
        for(var n = 0; n < tableArr.length; n++ ){
		  //initial
		  var tmp = new Array();
		  var tableVal = new Array();
	      for(var i = 0; i < $("#"+tableArr[n]).find("table").find("tr").length ; i++ ){
	        tmp.push(new Array());
		  }
		  
		  for(var i = 1; i < tmp.length ; i++ ){
		    $("#"+tableArr[n]).find("table").find("tr").eq(i).each( function(){
		      //input field + value
		      $(this).find("td").find("input:text").each(function(){			
	            tmp[i].push( $(this).val() );			
		      });
			  
		      //mutation control
			  var mut = new Array();
			  $(this).find("[name='multiSelect[]']").each( function(){
			    mut.push( $(this).val() );
			  });
			  if( mut[0].length > 0 ){
			    tmp[i].push( mut[0].join(mutationSplit) );
			  }
			  else{ 
			    tmp[i].push( '0' );
			  }
			  
		    });
		    //serial a row
		    tableVal.push( tmp[i].join(tmpSlipt) );
		  }
		  //serial a table
		  $("#uploadTable").append('<input type=\"hidden\" name=\"table'+n+'Arr\" value=\"' +tableVal.join(tableValSplit)+ '\">');
		}
		return true;
      }
	  else{ return false; }
    }

	function check_form(){
	  if( $("#url").val() === '' ){ 
		alert("please input the web url!");
		return false;
      }
	  var warn = 0;
	  $("#tableDiv").find("table").each( function(){
	    $(this).find("tr").find("td").find("input").each( function(){
		  if( $(this).val() === '' ){ warn +=1; }
		});
	  });
	  if( warn != 0 ){
		alert("there are "+warn+" empty name!\nplease enter all the text name!");
		return false;
	  }
	  return true;
	}
	
	function submit_text(){				
	  if($("#formtype").val()==="submit"){
        $('#page_content').submit();  
          
	  }
	  if($("#formtype").val()==="upload"){	
	    $("#upload").submit();
	  }
	}

	function run(){
	
		$.ajax({
			url: "runAjax.php",
			data:{
				submit_sql_id: $("#submit_sql_id").val()
			},
			type:"POST",
			datatype:"json",
			success: function(ms){
          		alert(ms);
          		var msg = jQuery.parseJSON(ms);
          		
          		if(msg['to_work']){
					//change to look result page
					setTimeout(function(){
						window.location.href = "result_page.php";
					}, 1000);
          		}else{
          			alert("上個網站測試仍在進行中...\n請稍待前一個測試完成再進行下一個測試");
          		}
			},
	        error: function(ms){
	        	var msg = jQuery.parseJSON(ms);
				alert(msg["out"]);
	        },
	        beforeSend:function(){
			    //start run=>already to check
	        }
		});
    }
	
	function form_submit(){
	  $("#formtype").val("submit");
	}
	
	function form_upload(){
	  $("#formtype").val("upload");
	}  
        
	 //<script type="text/javascript">    $('#aa').multiselect();</script>
