from sys import argv,exit
import socket
from utils import random_bytes_message,parse_argv
from time import time,sleep
from os import getpid
from struct import pack,unpack



class ICMPResponse():
	"""this is response from server"""

	def __init__(self,type,code,id,sequence,bytes_received):
		self._type = type
		self._code = code
		self._id = id
		self._sequence = sequence
		self._bytes_received = bytes_received

	@property
	def type(self):
		return self._type

	@property
	def code(self):
		return self._code

	@property
	def id(self):
		return self._id

	@property
	def sequence(self):
		return self._sequence
	
	@property
	def bytes_received(self):
		return self._bytes_received
	




class ICMPSocket():
	_ICMP_TYPE_ = 8


	def __init__(self,address):
		self.address = address


	def create_socket(self,ttl,timeout):
		#return socket with ttl and timeout
		soc = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
		soc.setsockopt(socket.IPPROTO_IP,socket.IP_TTL,ttl)
		soc.settimeout(timeout)
		return soc


	def _checksum(self, data):
		#this function is calculates the checksum
		sum = 0
		data += b'\x00'

		for i in range(0, len(data) - 1, 2):
			sum += (data[i] << 8) + data[i + 1]
			sum  = (sum & 0xffff) + (sum >> 16)

		sum = ~sum & 0xffff

		return sum


	def _create_package(self,id,sequence,payload):
#this function return package
#   Echo Request and Echo Reply messages                      RFC 792
#
#    0              1               2               3
#    0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
#   -----------------------------------------------------------------
#   |     Type      |     Code      |           Checksum            |
#   -----------------------------------------------------------------
#   |          					 Content					        |
#   -----------------------------------------------------------------
		
		_checksum = 0

		headers = pack("!2B3H",self._ICMP_TYPE_,0,_checksum,id,sequence)

		_checksum = self._checksum(headers + payload)

		headers = pack("!2B3H",self._ICMP_TYPE_,0,_checksum,id,sequence)

		return headers + payload


	def _parse_response(self,package):
		#this function parse response from server
		type,code = unpack("!2B",package[20:22])

		id,sequence = unpack("!2H",package[24:28])

		bytes_received = len(package) - 20

		response = ICMPResponse(
			type = type,
			code = code,
			id = id,
			sequence = sequence,
			bytes_received = bytes_received)

		return response


	def send(self,soc,id,sequence,payload):
		"""this function sends package to the server,
		waits for a response and calculates the time"""
		package = self._create_package(id,sequence,payload)
		soc.sendto(package,(self.address,0))
		
		start_time = time()
		try:
			response, _ = soc.recvfrom(1024)
		except socket.timeout:
			print("Превышено время ожидания")
			exit()

		total_time = time() - start_time

		response = self._parse_response(response)

		return (response,total_time)


class ICMP_Client(ICMPSocket):

	def __init__(self,address,timeout = 2,count = 4,ttl = 64):
		super().__init__(address)
		self.timeout = timeout
		self.count = count + 2
		self.ttl = ttl


	def ping(self):
		#This is "main" function
		#it's make all work
		min_t = float('inf')
		max_t = 0
		mid_t = 0
		received_packets = 0
		sended_packets = 0

		id = getpid()
		payload = random_bytes_message(56)
		sequence = 0

		soc = self.create_socket(ttl = self.ttl,timeout = self.timeout)

	
		print("Обмен пакетами с [{}],с 64 байтами данных.\n".format(self.address))

		n = self.count
		while n > 2 or n == True:

			try:
				sleep(0.7)

				if n == 1:
					sequence &= 0xFFFF
					response,time = self.send(soc,id,sequence,payload)
					time = round(time * 1000)

					if time < min_t:
						min_t = time
					elif time > max_t:
						max_t = time
					mid_t += time
					received_packets += 1
					sended_packets += 1

					sequence += 1

				elif n > 1:
					sequence &= 0xFFFF
					response,time = self.send(soc,id,sequence,payload)
					time = round(time * 1000)

					if time < min_t:
						min_t = time
					elif time > max_t:
						max_t = time
					mid_t += time
					received_packets += 1
					sended_packets += 1

					sequence += 1

					n -= 1

				print("Ответ от {}: число байт={}, время={}мс, TTL={}".format(self.address,64,time,self.ttl))
			
			except KeyboardInterrupt:
				break


		mid_t //= received_packets
		print("\nСтатистика: отправлено={}, получено={},потеряно={}".format(sended_packets,received_packets,sended_packets - received_packets))
		print("    Время приема-передачи: min={}мс, max={}мс, mid={}мс".format(min_t,max_t,mid_t))



class Applying_settings():
	def __init__(self,settings):
		self._settings = settings
		self.parse_setting()


	def _print_setting_info(self):
		#print settings from file
		with open("doc.txt",encoding = "utf-8") as file:
			print(file.read())


	def parse_setting(self):
		#parses settings, creates an ICMP client and calls the "ping" function
		if len(self._settings) == 0:
			self._print_setting_info()

		elif len(self._settings) == 1:
			try:
				address = socket.gethostbyname(self._settings["address"])
			except socket.gaierror:
				print("Несуществует такого узла\nПроверьте имя узла")
				exit()
			cl = ICMP_Client(address)
			cl.ping()

		else:
			try:
				_i = self._settings["-i"]
				_i = int(_i)
			except KeyError:
				_i = 64
			except ValueError:
				self._print_setting_info()
				return 0

			try:
				_w = self._settings["-w"]
				_w = float(_w)
			except KeyError:
				_w = 2
			except ValueError:
				self._print_setting_info()
				return 0

			try:
				_count = self._settings["-n"]
				_count = int(_count)
			except KeyError:
				_count = 4
			except ValueError:
				self._print_setting_info()
				return 0

			try:
				_count = self._settings["-t"]
				_count = - int(_count)
			except KeyError:
				pass
			except ValueError:
				self._print_setting_info()
				return 0

			address = socket.gethostbyname(self._settings["address"])
			cl = ICMP_Client(address,timeout = _w,count = _count,ttl = _i)
			cl.ping()




settings = parse_argv(argv)
cl = Applying_settings(settings)
