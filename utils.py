from random import choices

def random_bytes_message(size):
	#generate random bytes message

	message = choices(
		b"abcdefghijklmponqrstuvwxyz"
		b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		b"123456789",k = size)

	return bytes(message)


def parse_argv(argv):
	"""this function parce argv and return dictionary with flags"""
	setting_dict = {}

	if len(argv) == 1:
		return setting_dict

	else:
		if argv[-1].startswith("-"):
			return setting_dict
		else:
			setting_dict["address"] = argv[-1]


		for i in range(1,len(argv) - 2,2):
			try:
				setting_dict[argv[i]] = argv[i + 1]

			except IndexError:
				pass

	return setting_dict
