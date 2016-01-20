import urlparse

class Create_jmeter:
	def __init__(self,trace_list,dir_location,trace_number):
		self.trace = trace_list
		self.dir_location = dir_location
		self.trace_number = trace_number
		self.serial_prefix = 'b2g-monkey-'

	def write_jmeter(self):
		jmeter_testplan_start = \
			"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n
			<jmeterTestPlan version=\"1.2\" properties=\"2.1\">\n
			<hashTree>\n"""

		testplan_start = \
			"""<TestPlan guiclass=\"TestPlanGui\" testclass=\"TestPlan\" 
				testname=\"Test Plan\" enabled=\"true\">\n
			<stringProp name=\"TestPlan.comments\"></stringProp>\n
			<boolProp name=\"TestPlan.functional_mode\">false</boolProp>\n
			<boolProp name=\"TestPlan.serialize_threadgroups\">false</boolProp>\n
			<elementProp name=\"TestPlan.user_defined_variables\" 
				elementType=\"Arguments\" guiclass=\"ArgumentsPanel\" testclass=\"Arguments\" 
				testname=\"User Defined Variables\" enabled=\"true\">\n
			<collectionProp name=\"Arguments.arguments\" />\n
			</elementProp>\n
			<stringProp name=\"TestPlan.user_define_classpath\"></stringProp>\n
			</TestPlan>\n
			<hashTree>\n"""

		threadgroup_start = \
			"""<ThreadGroup guiclass=\"ThreadGroupGui\" testclass=\"ThreadGroup\" testname=\"Thread Group\" enabled=\"true\">\n
			<elementProp name=\"ThreadGroup.main_controller\" 
				elementType=\"LoopController\" guiclass=\"LoopControlPanel\" 
				testclass=\"LoopController\" testname=\"Loop Controller\" enabled=\"true\">\n
			<boolProp name=\"LoopController.continue_forever\">false</boolProp>\n
			<stringProp name=\"LoopController.loops\">1</stringProp>\n
			</elementProp>\n
			<stringProp name=\"ThreadGroup.num_threads\">1</stringProp>\n
			<stringProp name=\"ThreadGroup.ramp_time\">1</stringProp>\n
			<longProp name=\"ThreadGroup.start_time\">1281132211000</longProp>\n
			<longProp name=\"ThreadGroup.end_time\">1281132211000</longProp>\n
			<boolProp name=\"ThreadGroup.scheduler\">false</boolProp>\n
			<stringProp name=\"ThreadGroup.on_sample_error\">continue</stringProp>\n
			<stringProp name=\"ThreadGroup.duration\"></stringProp>\n
			<stringProp name=\"ThreadGroup.delay\"></stringProp>\n
			</ThreadGroup>\n
			<hashTree>\n"""

		cookiemanager = \
			"""<CookieManager guiclass=\"CookiePanel\" testclass=\"CookieManager\" 
				testname=\"HTTP Cookie Manager\" enabled=\"true\">\n
			<collectionProp name=\"CookieManager.cookies\" />\n
			<boolProp name=\"CookieManager.clearEachIteration\">false</boolProp>\n
			<stringProp name=\"CookieManager.policy\">rfc2109</stringProp>\n
			</CookieManager>\n
			<hashTree />\n"""

		arguments = \
			"""<Arguments guiclass=\"ArgumentsPanel\" testclass=\"Arguments\" 
				testname=\"User Defined Variables\" enabled=\"true\">\n
			<collectionProp name=\"Arguments.arguments\">\n
			<elementProp name=\"VIEWSTATE\" elementType=\"Argument\">\n
			<stringProp name=\"Argument.name\">VIEWSTATE</stringProp>\n
			<stringProp name=\"Argument.value\"></stringProp>\n
			<stringProp name=\"Argument.metadata\">=</stringProp>\n
			</elementProp>\n
			<elementProp name=\"jsessionid\" elementType=\"Argument\">\n
			<stringProp name=\"Argument.name\">jsessionid</stringProp>\n
			<stringProp name=\"Argument.value\"></stringProp>\n
			<stringProp name=\"Argument.metadata\">=</stringProp>\n
			</elementProp>\n
			</collectionProp>\n
			</Arguments>\n
			<hashTree />\n"""

		headermanager = \
			"""<HeaderManager guiclass=\"HeaderPanel\" testclass=\"HeaderManager\" 
				testname=\"HTTP Header Manager\" enabled=\"true\">\n
			<collectionProp name=\"HeaderManager.headers\">\n
			<elementProp name=\"\" elementType=\"Header\">\n
			<stringProp xml:space=\"preserve\" name=\"Header.name\">User-Agent</stringProp>\n
			<stringProp xml:space=\"preserve\" name=\"Header.value\">Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko</stringProp>\n
			</elementProp>\n
			<elementProp name=\"\" elementType=\"Header\">\n
			<stringProp xml:space=\"preserve\" name=\"Header.name\">Accept</stringProp>\n
			<stringProp xml:space=\"preserve\" name=\"Header.value\">image/jpeg, application/x-ms-application, image/gif, application/xaml+xml, image/pjpeg, application/x-ms-xbap, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*</stringProp>\n
			</elementProp>\n
			<elementProp name=\"\" elementType=\"Header\">\n
			<stringProp xml:space=\"preserve\" name=\"Header.name\">Accept-Language</stringProp>\n
			<stringProp xml:space=\"preserve\" name=\"Header.value\">zh-TW</stringProp>\n
			</elementProp>\n
			</collectionProp>\n
			</HeaderManager>\n
			<hashTree />\n"""

		loopcontroller_start = \
			"""<LoopController guiclass=\"LoopControlPanel\" testclass=\"LoopController\" testname=\"Step 1\" enabled=\"true\">\n
			<boolProp name=\"LoopController.continue_forever\">false</boolProp>\n
			<stringProp name=\"LoopController.loops\">1</stringProp>\n
			</LoopController>\n
			<hashTree>\n"""

		samplers = self.first_sampler()
		for n in xrange( len(self.trace["edges"]) ):
			samplers += self.http_sampler(n)

		loopcontroller_end = """</hashTree>\n"""
		threadgroup_end = """</hashTree>\n"""
		testplan_end = """</hashTree>\n"""
		jmeter_testplan_end = \
			"""</hashTree>\n
			</jmeterTestPlan>\n"""

		jmeter = jmeter_testplan_start + testplan_start + threadgroup_start + \
			cookiemanager + arguments + headermanager + samplers + \
			loopcontroller_end + threadgroup_end + testplan_end + jmeter_testplan_end

		fo = open(self.dir_location+"/jmeter"+str(self.trace_number)+".jmx","w")
		fo.write(jmeter)
		fo.close()


	def http_sampler(self, n):
		sampler_start = "<HTTPSampler guiclass=\"HttpTestSampleGui\" " + \
			"testclass=\"HTTPSampler\" enabled=\"true\""" testname=\"" + \
			self.trace["states"][n+1]["url"]+"\">\n"

		arguments = self.http_sampler_arguments(n)

		url = urlparse.urlparse(self.trace["states"][n+1]["url"])
		url_prop = "<stringProp name=\"HTTPSampler.domain\">"+url.netloc+"</stringProp>\n"
		url_prop += "<stringProp name=\"HTTPSampler.port\">"+url.port+"</stringProp>\n" \
			if url.port else "<stringProp name=\"HTTPSampler.port\"></stringProp>\n"			
		url_prop += "<stringProp name=\"HTTPSampler.protocol\">"+url.scheme+"</stringProp>\n" + \
			"<stringProp name=\"HTTPSampler.contentEncoding\"></stringProp>\n" + \
			"<stringProp name=\"HTTPSampler.path\">"+url.path+"</stringProp>\n"
		url_prop += "<stringProp name=\"HTTPSampler.method\">POST</stringProp>\n" \
			if len(self.trace["edges"][n]["inputs"])!=0 \
			else "<stringProp name=\"HTTPSampler.method\">GET</stringProp>\n"

		basic_prop = \
			"""<boolProp name=\"HTTPSampler.follow_redirects\">true</boolProp>\n
			<boolProp name=\"HTTPSampler.auto_redirects\">true</boolProp>\n
			<boolProp name=\"HTTPSampler.use_keepalive\">true</boolProp>\n
			<boolProp name=\"HTTPSampler.DO_MULTIPART_POST\">false</boolProp>\n
			<stringProp name=\"HTTPSampler.mimetype\"></stringProp>\n
			<stringProp name=\"HTTPSampler.monitor\">false</stringProp>\n
			<stringProp name=\"HTTPSampler.embedded_url_re\"></stringProp>\n"""

		sampler_end = \
			"""</HTTPSampler>\n
			<hashTree />\n"""
		sampler = sampler_start + arguments + url_prop + basic_prop + sampler_end
		return sampler

	def http_sampler_arguments(self, n):
		arguments_start = "<elementProp name=\"HTTPsampler.Arguments\" elementType=\"Arguments\" " + \
			"guiclass=\"HTTPArgumentsPanel\" testclass=\"Arguments\" " + \
			"testname=\"User Defined Variables\" enabled=\"true\">"+ self.trace["states"][n+1]["url"]+"\n"
		collection_start = "<collectionProp name=\"Arguments.arguments\">\n"

		collection_arguments = ""
		for each_input in self.trace["edges"][n]["inputs"]:
			name = str(each_input["name"])
			if name.startswith(self.serial_prefix) :
				continue
			collection_arguments += \
				"<elementProp elementType=\"HTTPArgument\" name=\""+name+"\">\n" + \
				"<boolProp name=\"HTTPArgument.always_encode\">true</boolProp>\n" + \
				"<stringProp name=\"Argument.value\">"+str(each_input["value"])+"</stringProp>\n" + \
				"<stringProp name=\"Argument.metadata\">=</stringProp>\n" + \
				"<boolProp name=\"HTTPArgument.use_equals\">true</boolProp>\n" + \
				"<stringProp name=\"Argument.name\">"+name+"</stringProp>\n" + \
				"</elementProp>\n"
		for each_select in self.trace["edges"][n]["selects"]:
			name = str(each_select["name"])
			if name.startswith(self.serial_prefix) :
				continue
			selected = int(each_select["selected"])
			value = str(each_select["value"][selected]) if len(each_select["value"]) > selected else ""
			collection_arguments += \
				"<elementProp elementType=\"HTTPArgument\" name=\""+name+"\">\n" + \
				"<boolProp name=\"HTTPArgument.always_encode\">true</boolProp>\n" + \
				"<stringProp name=\"Argument.value\">"+value+"</stringProp>\n" + \
				"<stringProp name=\"Argument.metadata\">=</stringProp>\n" + \
				"<boolProp name=\"HTTPArgument.use_equals\">true</boolProp>\n" + \
				"<stringProp name=\"Argument.name\">"+name+"</stringProp>\n" + \
				"</elementProp>\n"
		for each_radio in self.trace["edges"][n]["radios"]:
			name = str(each_radio["radio_name"])
			if name.startswith(self.serial_prefix) :
				continue
			selected = int(each_radio["radio_selected"])
			value = str(each_radio["radio_list"][selected]["value"]) if len(each_radio["radio_list"]) > selected else ""
			collection_arguments += \
				"<elementProp elementType=\"HTTPArgument\" name=\""+name+"\">\n" + \
				"<boolProp name=\"HTTPArgument.always_encode\">true</boolProp>\n" + \
				"<stringProp name=\"Argument.value\">"+value+"</stringProp>\n" + \
				"<stringProp name=\"Argument.metadata\">=</stringProp>\n" + \
				"<boolProp name=\"HTTPArgument.use_equals\">true</boolProp>\n" + \
				"<stringProp name=\"Argument.name\">"+name+"</stringProp>\n" + \
				"</elementProp>\n"
		for each_checkbox in self.trace["edges"][n]["checkboxes"]:
			name = str(each_checkbox["checkbox_name"])
			if name.startswith(self.serial_prefix) :
				continue
			selected_list = each_checkbox["checkbox_selected_list"]
			checkbox_list = each_checkbox["checkbox_list"]
			for c in selected_list:
				value = checkbox_list[int(c)]["value"] if len(checkbox_list) > int(c) else ""
				collection_arguments += \
					"<elementProp elementType=\"HTTPArgument\" name=\""+name+"\">\n" + \
					"<boolProp name=\"HTTPArgument.always_encode\">true</boolProp>\n" + \
					"<stringProp name=\"Argument.value\">"+value+"</stringProp>\n" + \
					"<stringProp name=\"Argument.metadata\">=</stringProp>\n" + \
					"<boolProp name=\"HTTPArgument.use_equals\">true</boolProp>\n" + \
					"<stringProp name=\"Argument.name\">"+name+"</stringProp>\n" + \
					"</elementProp>\n"

		collection_end = "</collectionProp>\n"			
		arguments_end = "</elementProp>\n"

		arguments = arguments_start + collection_start + collection_arguments + collection_end + arguments_end
		return arguments

	def first_sampler(self):
		sampler_start = "<HTTPSampler guiclass=\"HttpTestSampleGui\" " + \
			"testclass=\"HTTPSampler\" enabled=\"true\""" testname=\"" + \
			self.trace["states"][0]["url"]+"\">\n"

		arguments_start = "<elementProp name=\"HTTPsampler.Arguments\" elementType=\"Arguments\" " + \
			"guiclass=\"HTTPArgumentsPanel\" testclass=\"Arguments\" " + \
			"testname=\"User Defined Variables\" enabled=\"true\">"+ self.trace["states"][0]["url"]+"\n" 
		collection_start = "<collectionProp name=\"Arguments.arguments\">\n"
		collection_end = "</collectionProp>\n"			
		arguments_end = "</elementProp>\n"

		url = urlparse.urlparse(self.trace["states"][0]["url"])
		url_prop = "<stringProp name=\"HTTPSampler.domain\">"+url.netloc+"</stringProp>\n"
		url_prop += "<stringProp name=\"HTTPSampler.port\">"+url.port+"</stringProp>\n" \
			if url.port else "<stringProp name=\"HTTPSampler.port\"></stringProp>\n"			
		url_prop += "<stringProp name=\"HTTPSampler.protocol\">"+url.scheme+"</stringProp>\n" + \
			"<stringProp name=\"HTTPSampler.contentEncoding\"></stringProp>\n" + \
			"<stringProp name=\"HTTPSampler.path\">"+url.path+"</stringProp>\n"
		url_prop += "<stringProp name=\"HTTPSampler.method\">GET</stringProp>\n"

		basic_prop = \
			"""<boolProp name=\"HTTPSampler.follow_redirects\">true</boolProp>\n
			<boolProp name=\"HTTPSampler.auto_redirects\">true</boolProp>\n
			<boolProp name=\"HTTPSampler.use_keepalive\">true</boolProp>\n
			<boolProp name=\"HTTPSampler.DO_MULTIPART_POST\">false</boolProp>\n
			<stringProp name=\"HTTPSampler.mimetype\"></stringProp>\n
			<stringProp name=\"HTTPSampler.monitor\">false</stringProp>\n
			<stringProp name=\"HTTPSampler.embedded_url_re\"></stringProp>\n"""

		sampler_end = \
			"""</HTTPSampler>\n
			<hashTree />\n"""
		sampler = sampler_start + arguments_start + collection_start + collection_end + arguments_end + url_prop + basic_prop + sampler_end
		return sampler
