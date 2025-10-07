try:
	long # Python 2
except NameError:
	long = int # Python 3

def UUID1(ori_uuid1, ori_nanoseconds_received, nanoseconds_received, ClockSequence=None):
	import uuid, time

	if uuid.UUID(ori_uuid1).version == 1 and type(ori_nanoseconds_received) in [int, long] and type(nanoseconds_received) in [int, long]:
		# 0x01b21dd213814000 is the number of 100-ns intervals between the UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
		# nanoseconds = int(time.time() * 1e9)
		# uuid1_time = int(nanoseconds/100) + 0x01b21dd213814000
		uuid1_PartOneTwoThree = []
		uuid1_time_received = int(nanoseconds_received/100) + 0x01b21dd213814000
		ori_uuid1_time_received = int(ori_nanoseconds_received/100) + 0x01b21dd213814000
		delayTime_received = ori_uuid1_time_received - int(ori_uuid1.split("-")[2][1:] + ori_uuid1.split("-")[1] + ori_uuid1.split("-")[0], 16)
		for i in range(delayTime_received, -1, -1):
			uuid1_TimeLow = hex(uuid1_time_received-i)[2:][7:15]
			uuid1_TimeMid = hex(uuid1_time_received-i)[2:][3:7]
			uuid1_VersionAndTimeHigh = "1" + hex(uuid1_time_received-i)[2:][0:3]
			uuid1_PartOneTwoThree.append(uuid1_TimeLow + "-" + uuid1_TimeMid + "-" + uuid1_VersionAndTimeHigh)


		if type(ClockSequence) in [list, range]:
			uuid1_ClockSequence = [hex(i)[2:].zfill(4) for i in ClockSequence]
		else:
			variant = ori_uuid1.split("-")[3][0]
			if 0x0 <= int(variant, 16) <= 0x7:
				uuid1_ClockSequence = [hex(i)[2:].zfill(4) for i in range(0x0000, 0x8000)]
			elif 0x8 <= int(variant, 16) <= 0xb:
				uuid1_ClockSequence = [hex(i)[2:].zfill(4) for i in range(0x8000, 0xc000)]
			elif 0xc <= int(variant, 16) <= 0xd:
				uuid1_ClockSequence = [hex(i)[2:].zfill(4) for i in range(0xc000, 0xe000)]
			elif int(variant, 16) == 0xe:
				uuid1_ClockSequence = [hex(i)[2:].zfill(4) for i in range(0xe000, 0xf000)]
			else:
				uuid1_ClockSequence = [hex(i)[2:].zfill(4) for i in range(0xf000, 0xffff)]


		uuid1_NodeID = ori_uuid1.split("-")[4]

		return {
			"PartOneTwoThree": uuid1_PartOneTwoThree,
			"PartFour": uuid1_ClockSequence,
			"PartFive": uuid1_NodeID
		}
	else:
		return {
			"PartOneTwoThree": [],
			"PartFour": [],
			"PartFive": ""
		}