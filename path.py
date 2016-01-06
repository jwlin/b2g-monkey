import json, codecs, sys, os
import jmeter

'''try:
	with codecs.open(sys.argv[1]) as json_file:
		json_data = json.load(json_file)
except Exception as e:
			print( "[ERROR] read JSON failed", e)'''
			
#try:
with codecs.open( sys.argv[1] ) as json_file:
		json_data = json.load(json_file)
		trace_number = int(sys.argv[3])
		j = jmeter.Create_jmeter(json_data["traces"][trace_number],sys.argv[2],trace_number)
		j.write_jmeter()
#except Exception as e:#
#	print( sys.argv[1] ,"[ERROR] read JSON failed", e)