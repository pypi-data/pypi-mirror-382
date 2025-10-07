def Sniper(InjectionPoints, Payloads):
	'''
	- The data type of "InjectionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The "Payloads" has length "1"
	- The data type of the first element of Payloads must be a "list"
	'''
	if type(InjectionPoints) != list \
	or type(Payloads) != list \
	or len(Payloads) != 1 \
	or type(Payloads[0]) != list:
		exit("[-] Invalid InjectionPoints or Payloads")

	try:
		testcases = list()
		for injection_point in InjectionPoints:
			if type(injection_point) != str:
				exit("[-] Invalid InjectionPoints: {}".format(injection_point))

			for payload in Payloads[0]:
				testcases.append({ injection_point: payload })
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)



def Batteringram(InjectionPoints, Payloads):
	'''
	- The data type of "InjectionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The "Payloads" has length "1"
	- The data type of the first element of Payloads must be a "list"
	'''
	if type(InjectionPoints) != list \
	or type(Payloads) != list \
	or len(Payloads) != 1 \
	or type(Payloads[0]) != list:
		exit("[-] Invalid InjectionPoints or Payloads")

	try:
		testcases = list()
		for payload in Payloads[0]:
			tmp = dict()
			for injection_point in InjectionPoints:
				if type(injection_point) != str:
					exit("[-] Invalid InjectionPoints: {}".format(injection_point))

				tmp[injection_point] = payload
			testcases.append(tmp)
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)



def Pitchfork(InjectionPoints, Payloads):
	'''
	- The data type of "InjectionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The length of "Payloads" is equal to the length of "InjectionPoints"
	- The data type of each Payloads element must be a "list" of equal length
	'''
	if type(InjectionPoints) != list \
	or type(Payloads) != list \
	or len(InjectionPoints) != len(Payloads) \
	or len([1 for i in Payloads if type(i)==list]) != len(Payloads) \
	or len(set([len(i) for i in Payloads])) != 1:
		exit("[-] Invalid InjectionPoints or Payloads")

	try:
		testcases = list()
		for j in range(len(Payloads[0])):
			tmp = dict()
			for i in range(len(InjectionPoints)):
				if type(InjectionPoints[i]) != str:
					exit("[-] Invalid InjectionPoints: {}".format(InjectionPoints[i]))

				tmp[InjectionPoints[i]] = Payloads[i][j]
			testcases.append(tmp)
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)



def Clusterbomb(InjectionPoints, Payloads):
	def generate_combinations(Payloads):
		if len(Payloads) == 1:
			return [[Payloads[0][j]] for j in range(len(Payloads[0]))]
		else:
			sub_combinations = generate_combinations(Payloads[1:])
			combinations = []
			for j in range(len(Payloads[0])):
				for sub_combination in sub_combinations:
					combinations.append([Payloads[0][j]] + sub_combination)
			return combinations

	'''
	- The data type of "InjectionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The length of "Payloads" is equal to the length of "InjectionPoints"
	- The data type of each Payloads element must be a "list"
	'''
	if type(InjectionPoints) != list \
	or type(Payloads) != list \
	or len(InjectionPoints) != len(Payloads) \
	or len([1 for i in Payloads if type(i)==list]) != len(Payloads):
		exit("[-] Invalid InjectionPoints or Payloads")

	try:
		testcases = list()
		for tc in generate_combinations(Payloads):
			tmp = dict()
			for i in range(len(InjectionPoints)):
				if type(InjectionPoints[i]) != str:
					exit("[-] Invalid InjectionPoints: {}".format(InjectionPoints[i]))

				tmp[InjectionPoints[i]] = tc[i]
			testcases.append(tmp)
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)