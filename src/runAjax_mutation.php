<?php   
  $folder_path = "/var/www/python/trace/".$_POST['dirname']."/mutant";
  $dirname = "mutant".$_POST['trace_number']."";
  $configuration = "/var/www/python/trace/".$_POST['dirname']."/config.json";
  $traces = "/var/www/python/trace/".$_POST['dirname']."/traces.json";
  $cmd = 'cd /var/www/python && python controller.py 2 '.$folder_path.' '.$dirname.' '.$configuration.' '.$traces.' '.$_POST['trace_number'].' '.$_POST['method'].' '.$_POST['mode'].' '.$_POST['max'].' > /dev/null 2>/dev/null &';
  $run = shell_exec($cmd);
  
  $return['run'] = $run;
  $return['cmd'] = $cmd;
  echo json_encode($return);
?>