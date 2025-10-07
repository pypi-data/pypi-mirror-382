import json_duplicate_keys as jdks

class initQR:
	def __init__(self, QR_Type, UnknownFields={}):
		self.QR_Type = QR_Type
		self.QR = jdks.loads("{}", ordered_dict=True)

		self.QR.set("00", jdks.loads('{ "name":"PayloadFormatIndicator", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("01", jdks.loads('{ "name":"PointOfInitiationMethod", "value":"" }', ordered_dict=True).getObject())


		if self.QR_Type == "VNPAYQR":
			self.QR.set("26", jdks.loads('{ "name":"MerchantAccountInformation", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("26||subTag||00", jdks.loads('{ "name":"GUID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("26||subTag||01", jdks.loads('{ "name":"MerchantID", "value":"" }', ordered_dict=True).getObject())

		elif self.QR_Type in ["VietQR", "MoMo"]:
			self.QR.set("38", jdks.loads('{ "name":"MerchantAccountInformation", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("38||subTag||00", jdks.loads('{ "name":"GUID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("38||subTag||01", jdks.loads('{ "name":"BeneficiaryOrganization", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("38||subTag||01||subTag||00", jdks.loads('{ "name":"BeneficiaryID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("38||subTag||01||subTag||01", jdks.loads('{ "name":"ReceiverNumber", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("38||subTag||02", jdks.loads('{ "name":"ServiceCode", "value":"" }', ordered_dict=True).getObject())

		elif self.QR_Type == "KHQR_Individual":
			self.QR.set("29", jdks.loads('{ "name":"MerchantAccountInformation", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||00", jdks.loads('{ "name":"BakongAccountID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||01", jdks.loads('{ "name":"AccountInformation", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||02", jdks.loads('{ "name":"AcquiringBank", "value":"" }', ordered_dict=True).getObject())

		elif self.QR_Type == "KHQR_Corporate":
			self.QR.set("30", jdks.loads('{ "name":"MerchantAccountInformation", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||00", jdks.loads('{ "name":"BakongAccountID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||01", jdks.loads('{ "name":"MerchantID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||02", jdks.loads('{ "name":"AcquiringBank", "value":"" }', ordered_dict=True).getObject())
		
		elif self.QR_Type == "ThaiQR_CREDIT_TRANSFER":
			self.QR.set("29", jdks.loads('{ "name":"MerchantAccountInformation", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||00", jdks.loads('{ "name":"AID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||01", jdks.loads('{ "name":"PhoneNumber", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||02", jdks.loads('{ "name":"NationalID_or_TaxID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||03", jdks.loads('{ "name":"eWalletID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||04", jdks.loads('{ "name":"BankAccount", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("29||subTag||05", jdks.loads('{ "name":"OTA", "value":"" }', ordered_dict=True).getObject())

		elif self.QR_Type == "ThaiQR_BILL_PAYMENT":
			self.QR.set("30", jdks.loads('{ "name":"MerchantAccountInformation", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||00", jdks.loads('{ "name":"AID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||01", jdks.loads('{ "name":"BillerID", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||02", jdks.loads('{ "name":"Reference_1", "value":"" }', ordered_dict=True).getObject())
			self.QR.set("30||subTag||03", jdks.loads('{ "name":"Reference_2", "value":"" }', ordered_dict=True).getObject())


		self.QR.set("52", jdks.loads('{ "name":"MerchantCategoryCode", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("53", jdks.loads('{ "name":"TransactionCurrency", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("54", jdks.loads('{ "name":"TransactionAmount", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("55", jdks.loads('{ "name":"TipOrConvenienceIndicator", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("56", jdks.loads('{ "name":"ValueOfConvenienceFeeFixed", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("57", jdks.loads('{ "name":"ValueOfConvenienceFeePercentage", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("58", jdks.loads('{ "name":"CountryCode", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("59", jdks.loads('{ "name":"MerchantName", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("60", jdks.loads('{ "name":"MerchantCity", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("61", jdks.loads('{ "name":"PostalCode", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62", jdks.loads('{ "name":"AdditionalDataFieldTemplate", "value":"", "subTag":{} }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||01", jdks.loads('{ "name":"BillNumber", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||02", jdks.loads('{ "name":"MobileNumber", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||03", jdks.loads('{ "name":"StoreLabel", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||04", jdks.loads('{ "name":"LoyaltyNumber", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||05", jdks.loads('{ "name":"ReferenceLabel", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||06", jdks.loads('{ "name":"CustomerLabel", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||07", jdks.loads('{ "name":"TerminalLabel", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||08", jdks.loads('{ "name":"PurposeOfTransaction", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("62||subTag||09", jdks.loads('{ "name":"AdditionalConsumerDataRequest", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("63", jdks.loads('{ "name":"CRC", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("64", jdks.loads('{ "name":"MerchantInformation_LanguageTemplate", "value":"", "subTag":{} }', ordered_dict=True).getObject())
		self.QR.set("64||subTag||00", jdks.loads('{ "name":"LanguagePreference", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("64||subTag||01", jdks.loads('{ "name":"MerchantName_AlternateLanguage", "value":"" }', ordered_dict=True).getObject())
		self.QR.set("64||subTag||02", jdks.loads('{ "name":"MerchantCity_AlternateLanguage", "value":"" }', ordered_dict=True).getObject())

		if self.QR_Type == "MoMo":
			self.QR.set("80", jdks.loads('{ "name":"LastThreeDigitsOfPhoneNumber", "value":"" }', ordered_dict=True).getObject())

		if self.QR_Type in ["KHQR_Individual", "KHQR_Corporate"]:
			self.QR.set("99", jdks.loads('{ "name":"Timestamp", "value":"", "subTag":{} }', ordered_dict=True).getObject())
			self.QR.set("99||subTag||00", jdks.loads('{ "name":"timestamp", "value":"" }', ordered_dict=True).getObject())


		UnknownFields = jdks.JSON_DUPLICATE_KEYS(UnknownFields).filter_keys("^\\d+\\|\\|(?:subTag\\|\\|\\d+\\|\\|)*name$").getObject()
		for k in UnknownFields:
			self.QR.update(k[:-6], jdks.loads('{ "name":"'+UnknownFields[k]+'","value":"" }').getObject(), allow_new_key=True)



	def parse(self, QR_String, currentKey=""):
		while len(QR_String) > 0:
			try:
				TAG = LENGTH = VALUE = ""
				TAG = QR_String[:2]; QR_String = QR_String[2:]
				LENGTH_STR = QR_String[:2]; QR_String = QR_String[2:]
				LENGTH = int(LENGTH_STR)
				VALUE = QR_String[:LENGTH]; QR_String = QR_String[LENGTH:]

				if self.QR.get(currentKey+TAG)["value"] == "JSON_DUPLICATE_KEYS_ERROR":
					self.QR.set(currentKey+TAG, jdks.loads('{ "name":"UnknownField", "value":"'+TAG+LENGTH_STR+VALUE+'" }', ordered_dict=True).getObject())
				else:
					self.QR.update(currentKey+TAG+"||value", VALUE)
					if self.QR.get(currentKey+TAG+"||subTag")["value"] != "JSON_DUPLICATE_KEYS_ERROR":
						self.parse(VALUE, currentKey=self.QR.get(currentKey+TAG+"||subTag")["name"]+"||")
			except Exception as e:
				print("- currentKey: {}".format(currentKey))
				print("- TAG: {}".format(TAG))
				print("- LENGTH: {}".format(LENGTH_STR))
				print("- VALUE: {}".format(VALUE))
				return

		if currentKey == "":
			QRObj = jdks.loads("{}", ordered_dict=True)

			QR_byKeys = self.QR.filter_keys("^\\d+\\|\\|(?:subTag\\|\\|\\d+\\|\\|)*name$", ordered_dict=True)
			for k in QR_byKeys.getObject():
				kName = []
				QRObj_kName = []
				tags = k.split("||name",1)[0].split("||subTag||")
				for i in range(len(tags)):
					kName.append(tags[i])
					name = self.QR.get("||subTag||".join(kName)+"||name")["value"]
					value = self.QR.get("||subTag||".join(kName)+"||value")["value"]
					QRObj_kName.append(name)
					if len(value) > 0:
						if len(tags) == 1 or i == len(tags)-1:
							QRObj.update("||".join(QRObj_kName), value, allow_new_key=True, ordered_dict=True)
						elif type(QRObj.get("||".join(QRObj_kName))["value"]) != dict:
							QRObj.update("||".join(QRObj_kName), {}, allow_new_key=True, ordered_dict=True)
			return QRObj



	def unparse(self, QRObj, update_CRC=True):
		def calculate_crc16_ccitt_false(data):
			crc = 0xFFFF
			polynomial = 0x1021
			for byte in data:
				crc ^= (ord(byte) << 8)
				for _ in range(8):
					if crc & 0x8000:
						crc = (crc << 1) ^ polynomial
					else:
						crc <<= 1
				crc &= 0xFFFF
			return "{:04X}".format(crc)

		QR_String = ""

		TAG_00 = QRObj.get("PayloadFormatIndicator")
		if TAG_00["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_00["value"])) > 0: QR_String += "{}{:02}{}".format("00", len(str(TAG_00["value"])), str(TAG_00["value"]))

		TAG_01 = QRObj.get("PointOfInitiationMethod")
		if TAG_01["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_01["value"])) > 0: QR_String += "{}{:02}{}".format("01", len(str(TAG_01["value"])), str(TAG_01["value"]))

		if self.QR_Type == "VNPAYQR":
			TAG_26 = QRObj.get("MerchantAccountInformation")
			if TAG_26["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_26["value"])) > 0:
				TAG_26_val = ""
				TAG_2600 = QRObj.get("MerchantAccountInformation||GUID")
				if TAG_2600["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2600["value"])) > 0: TAG_26_val += "{}{:02}{}".format("00", len(str(TAG_2600["value"])), str(TAG_2600["value"]))

				TAG_2601 = QRObj.get("MerchantAccountInformation||MerchantID")
				if TAG_2601["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2601["value"])) > 0: TAG_26_val += "{}{:02}{}".format("01", len(str(TAG_2601["value"])), str(TAG_2601["value"]))

				for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|UnknownField").getObject():
					TAG_26_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("26", len(TAG_26_val), TAG_26_val)
		elif self.QR_Type in ["VietQR", "MoMo"]:
			TAG_38 = QRObj.get("MerchantAccountInformation")
			if TAG_38["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_38["value"])) > 0:
				TAG_38_val = ""
				TAG_3800 = QRObj.get("MerchantAccountInformation||GUID")
				if TAG_3800["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3800["value"])) > 0: TAG_38_val += "{}{:02}{}".format("00", len(str(TAG_3800["value"])), str(TAG_3800["value"]))

				TAG_3801 = QRObj.get("MerchantAccountInformation||BeneficiaryOrganization")
				if TAG_3801["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3801["value"])) > 0:
					TAG_3801_val = ""
					TAG_380100 = QRObj.get("MerchantAccountInformation||BeneficiaryOrganization||BeneficiaryID")
					if TAG_380100["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_380100["value"])) > 0: TAG_3801_val += "{}{:02}{}".format("00", len(str(TAG_380100["value"])), str(TAG_380100["value"]))

					TAG_380101 = QRObj.get("MerchantAccountInformation||BeneficiaryOrganization||ReceiverNumber")
					if TAG_380101["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_380101["value"])) > 0: TAG_3801_val += "{}{:02}{}".format("01", len(str(TAG_380101["value"])), str(TAG_380101["value"]))

					for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|BeneficiaryOrganization\\|\\|UnknownField").getObject():
						TAG_3801_val += str(QRObj.get(unknownKey)["value"])

					TAG_38_val += "{}{:02}{}".format("01", len(TAG_3801_val), TAG_3801_val)

				TAG_3802 = QRObj.get("MerchantAccountInformation||ServiceCode")
				if TAG_3802["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3802["value"])) > 0: TAG_38_val += "{}{:02}{}".format("02", len(str(TAG_3802["value"])), str(TAG_3802["value"]))

				for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|UnknownField").getObject():
					TAG_38_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("38", len(TAG_38_val), TAG_38_val)
		elif self.QR_Type == "KHQR_Individual":
			TAG_29 = QRObj.get("MerchantAccountInformation")
			if TAG_29["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_29["value"])) > 0:
				TAG_29_val = ""
				TAG_2900 = QRObj.get("MerchantAccountInformation||BakongAccountID")
				if TAG_2900["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2900["value"])) > 0: TAG_29_val += "{}{:02}{}".format("00", len(str(TAG_2900["value"])), str(TAG_2900["value"]))

				TAG_2901 = QRObj.get("MerchantAccountInformation||AccountInformation")
				if TAG_2901["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2901["value"])) > 0: TAG_29_val += "{}{:02}{}".format("01", len(str(TAG_2901["value"])), str(TAG_2901["value"]))

				TAG_2902 = QRObj.get("MerchantAccountInformation||AcquiringBank")
				if TAG_2902["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2902["value"])) > 0: TAG_29_val += "{}{:02}{}".format("02", len(str(TAG_2902["value"])), str(TAG_2902["value"]))

				for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|UnknownField").getObject():
					TAG_29_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("29", len(TAG_29_val), TAG_29_val)
		elif self.QR_Type == "KHQR_Corporate":
			TAG_30 = QRObj.get("MerchantAccountInformation")
			if TAG_30["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_30["value"])) > 0:
				TAG_30_val = ""
				TAG_3000 = QRObj.get("MerchantAccountInformation||BakongAccountID")
				if TAG_3000["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3000["value"])) > 0: TAG_30_val += "{}{:02}{}".format("00", len(str(TAG_3000["value"])), str(TAG_3000["value"]))

				TAG_3001 = QRObj.get("MerchantAccountInformation||MerchantID")
				if TAG_3001["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3001["value"])) > 0: TAG_30_val += "{}{:02}{}".format("01", len(str(TAG_3001["value"])), str(TAG_3001["value"]))

				TAG_3002 = QRObj.get("MerchantAccountInformation||AcquiringBank")
				if TAG_3002["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3002["value"])) > 0: TAG_30_val += "{}{:02}{}".format("02", len(str(TAG_3002["value"])), str(TAG_3002["value"]))

				for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|UnknownField").getObject():
					TAG_30_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("30", len(TAG_30_val), TAG_30_val)
		elif self.QR_Type == "ThaiQR_CREDIT_TRANSFER":
			TAG_29 = QRObj.get("MerchantAccountInformation")
			if TAG_29["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_29["value"])) > 0:
				TAG_29_val = ""
				TAG_2900 = QRObj.get("MerchantAccountInformation||AID")
				if TAG_2900["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2900["value"])) > 0: TAG_29_val += "{}{:02}{}".format("00", len(str(TAG_2900["value"])), str(TAG_2900["value"]))

				TAG_2901 = QRObj.get("MerchantAccountInformation||PhoneNumber")
				if TAG_2901["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2901["value"])) > 0: TAG_29_val += "{}{:02}{}".format("01", len(str(TAG_2901["value"])), str(TAG_2901["value"]))

				TAG_2902 = QRObj.get("MerchantAccountInformation||NationalID_or_TaxID")
				if TAG_2902["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2902["value"])) > 0: TAG_29_val += "{}{:02}{}".format("02", len(str(TAG_2902["value"])), str(TAG_2902["value"]))

				TAG_2903 = QRObj.get("MerchantAccountInformation||eWalletID")
				if TAG_2903["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2903["value"])) > 0: TAG_29_val += "{}{:02}{}".format("03", len(str(TAG_2903["value"])), str(TAG_2903["value"]))

				TAG_2904 = QRObj.get("MerchantAccountInformation||BankAccount")
				if TAG_2904["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2904["value"])) > 0: TAG_29_val += "{}{:02}{}".format("04", len(str(TAG_2904["value"])), str(TAG_2904["value"]))

				TAG_2905 = QRObj.get("MerchantAccountInformation||OTA")
				if TAG_2905["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_2905["value"])) > 0: TAG_29_val += "{}{:02}{}".format("05", len(str(TAG_2905["value"])), str(TAG_2905["value"]))

				for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|UnknownField").getObject():
					TAG_29_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("29", len(TAG_29_val), TAG_29_val)
		elif self.QR_Type == "ThaiQR_BILL_PAYMENT":
			TAG_30 = QRObj.get("MerchantAccountInformation")
			if TAG_30["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_30["value"])) > 0:
				TAG_30_val = ""
				TAG_3000 = QRObj.get("MerchantAccountInformation||AID")
				if TAG_3000["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3000["value"])) > 0: TAG_30_val += "{}{:02}{}".format("00", len(str(TAG_3000["value"])), str(TAG_3000["value"]))

				TAG_3001 = QRObj.get("MerchantAccountInformation||BillerID")
				if TAG_3001["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3001["value"])) > 0: TAG_30_val += "{}{:02}{}".format("01", len(str(TAG_3001["value"])), str(TAG_3001["value"]))

				TAG_3002 = QRObj.get("MerchantAccountInformation||Reference_1")
				if TAG_3002["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3002["value"])) > 0: TAG_30_val += "{}{:02}{}".format("02", len(str(TAG_3002["value"])), str(TAG_3002["value"]))

				TAG_3003 = QRObj.get("MerchantAccountInformation||Reference_2")
				if TAG_3003["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_3003["value"])) > 0: TAG_30_val += "{}{:02}{}".format("03", len(str(TAG_3003["value"])), str(TAG_3003["value"]))

				for unknownKey in QRObj.filter_keys("^MerchantAccountInformation\\|\\|UnknownField").getObject():
					TAG_30_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("30", len(TAG_30_val), TAG_30_val)

		TAG_52 = QRObj.get("MerchantCategoryCode")
		if TAG_52["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_52["value"])) > 0: QR_String += "{}{:02}{}".format("52", len(str(TAG_52["value"])), str(TAG_52["value"]))

		TAG_53 = QRObj.get("TransactionCurrency")
		if TAG_53["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_53["value"])) > 0: QR_String += "{}{:02}{}".format("53", len(str(TAG_53["value"])), str(TAG_53["value"]))

		TAG_54 = QRObj.get("TransactionAmount")
		if TAG_54["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_54["value"])) > 0: QR_String += "{}{:02}{}".format("54", len(str(TAG_54["value"])), str(TAG_54["value"]))

		TAG_55 = QRObj.get("TipOrConvenienceIndicator")
		if TAG_55["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_55["value"])) > 0: QR_String += "{}{:02}{}".format("55", len(str(TAG_55["value"])), str(TAG_55["value"]))

		TAG_56 = QRObj.get("ValueOfConvenienceFeeFixed")
		if TAG_56["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_56["value"])) > 0: QR_String += "{}{:02}{}".format("56", len(str(TAG_56["value"])), str(TAG_56["value"]))

		TAG_57 = QRObj.get("ValueOfConvenienceFeePercentage")
		if TAG_57["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_57["value"])) > 0: QR_String += "{}{:02}{}".format("57", len(str(TAG_57["value"])), str(TAG_57["value"]))

		TAG_58 = QRObj.get("CountryCode")
		if TAG_58["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_58["value"])) > 0: QR_String += "{}{:02}{}".format("58", len(str(TAG_58["value"])), str(TAG_58["value"]))

		TAG_59 = QRObj.get("MerchantName")
		if TAG_59["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_59["value"])) > 0: QR_String += "{}{:02}{}".format("59", len(str(TAG_59["value"])), str(TAG_59["value"]))

		TAG_60 = QRObj.get("MerchantCity")
		if TAG_60["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_60["value"])) > 0: QR_String += "{}{:02}{}".format("60", len(str(TAG_60["value"])), str(TAG_60["value"]))

		TAG_61 = QRObj.get("PostalCode")
		if TAG_61["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_61["value"])) > 0: QR_String += "{}{:02}{}".format("61", len(str(TAG_61["value"])), str(TAG_61["value"]))

		TAG_62 = QRObj.get("AdditionalDataFieldTemplate")
		if TAG_62["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_62["value"])) > 0:
			TAG_62_val = ""
			TAG_6201 = QRObj.get("AdditionalDataFieldTemplate||BillNumber")
			if TAG_6201["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6201["value"])) > 0: TAG_62_val += "{}{:02}{}".format("01", len(str(TAG_6201["value"])), str(TAG_6201["value"]))

			TAG_6202 = QRObj.get("AdditionalDataFieldTemplate||MobileNumber")
			if TAG_6202["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6202["value"])) > 0: TAG_62_val += "{}{:02}{}".format("02", len(str(TAG_6202["value"])), str(TAG_6202["value"]))

			TAG_6203 = QRObj.get("AdditionalDataFieldTemplate||StoreLabel")
			if TAG_6203["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6203["value"])) > 0: TAG_62_val += "{}{:02}{}".format("03", len(str(TAG_6203["value"])), str(TAG_6203["value"]))

			TAG_6204 = QRObj.get("AdditionalDataFieldTemplate||LoyaltyNumber")
			if TAG_6204["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6204["value"])) > 0: TAG_62_val += "{}{:02}{}".format("04", len(str(TAG_6204["value"])), str(TAG_6204["value"]))

			TAG_6205 = QRObj.get("AdditionalDataFieldTemplate||ReferenceLabel")
			if TAG_6205["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6205["value"])) > 0: TAG_62_val += "{}{:02}{}".format("05", len(str(TAG_6205["value"])), str(TAG_6205["value"]))

			TAG_6206 = QRObj.get("AdditionalDataFieldTemplate||CustomerLabel")
			if TAG_6206["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6206["value"])) > 0: TAG_62_val += "{}{:02}{}".format("06", len(str(TAG_6206["value"])), str(TAG_6206["value"]))

			TAG_6207 = QRObj.get("AdditionalDataFieldTemplate||TerminalLabel")
			if TAG_6207["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6207["value"])) > 0: TAG_62_val += "{}{:02}{}".format("07", len(str(TAG_6207["value"])), str(TAG_6207["value"]))

			TAG_6208 = QRObj.get("AdditionalDataFieldTemplate||PurposeOfTransaction")
			if TAG_6208["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6208["value"])) > 0: TAG_62_val += "{}{:02}{}".format("08", len(str(TAG_6208["value"])), str(TAG_6208["value"]))

			TAG_6209 = QRObj.get("AdditionalDataFieldTemplate||AdditionalConsumerDataRequest")
			if TAG_6209["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6209["value"])) > 0: TAG_62_val += "{}{:02}{}".format("09", len(str(TAG_6209["value"])), str(TAG_6209["value"]))

			for unknownKey in QRObj.filter_keys("^AdditionalDataFieldTemplate\\|\\|UnknownField").getObject():
				TAG_62_val += str(QRObj.get(unknownKey)["value"])

			QR_String += "{}{:02}{}".format("62", len(TAG_62_val), TAG_62_val)

		TAG_64 = QRObj.get("MerchantInformation_LanguageTemplate")
		if TAG_64["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_64["value"])) > 0:
			TAG_64_val = ""
			TAG_6400 = QRObj.get("MerchantInformation_LanguageTemplate||LanguagePreference")
			if TAG_6400["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6400["value"])) > 0: TAG_64_val += "{}{:02}{}".format("00", len(str(TAG_6400["value"])), str(TAG_6400["value"]))

			TAG_6401 = QRObj.get("MerchantInformation_LanguageTemplate||MerchantName_AlternateLanguage")
			if TAG_6401["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6401["value"])) > 0: TAG_64_val += "{}{:02}{}".format("01", len(str(TAG_6401["value"])), str(TAG_6401["value"]))

			TAG_6402 = QRObj.get("MerchantInformation_LanguageTemplate||MerchantCity_AlternateLanguage")
			if TAG_6402["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_6402["value"])) > 0: TAG_64_val += "{}{:02}{}".format("02", len(str(TAG_6402["value"])), str(TAG_6402["value"]))

			for unknownKey in QRObj.filter_keys("^MerchantInformation_LanguageTemplate\\|\\|UnknownField").getObject():
				TAG_64_val += str(QRObj.get(unknownKey)["value"])

			QR_String += "{}{:02}{}".format("64", len(TAG_64_val), TAG_64_val)

		if self.QR_Type == "MoMo":
			TAG_80 = QRObj.get("LastThreeDigitsOfPhoneNumber")
			if TAG_80["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_80["value"])) > 0: QR_String += "{}{:02}{}".format("80", len(str(TAG_80["value"])), str(TAG_80["value"]))

		if self.QR_Type in ["KHQR_Individual", "KHQR_Corporate"]:
			TAG_99 = QRObj.get("Timestamp")
			if TAG_99["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_99["value"])) > 0:
				TAG_99_val = ""
				TAG_9900 = QRObj.get("Timestamp||timestamp")
				if TAG_9900["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_9900["value"])) > 0: TAG_99_val += "{}{:02}{}".format("00", len(str(TAG_9900["value"])), str(TAG_9900["value"]))

				for unknownKey in QRObj.filter_keys("^Timestamp\\|\\|UnknownField").getObject():
					TAG_99_val += str(QRObj.get(unknownKey)["value"])

				QR_String += "{}{:02}{}".format("99", len(TAG_99_val), TAG_99_val)

		for unknownKey in QRObj.filter_keys("^UnknownField").getObject():
			QR_String += str(QRObj.get(unknownKey)["value"])

		if update_CRC:
			QR_String += "6304"
			QR_String += calculate_crc16_ccitt_false(QR_String)
		else:
			TAG_63 = QRObj.get("CRC")
			if TAG_63["value"] != "JSON_DUPLICATE_KEYS_ERROR" and len(str(TAG_63["value"])) > 0: QR_String += "{}{:02}{}".format("63", len(str(TAG_63["value"])), str(TAG_63["value"]))

		return QR_String