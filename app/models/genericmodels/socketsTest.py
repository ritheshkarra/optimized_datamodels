import socket
import sys

class socketsTest:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print(s)
	host = '127.0.0.1'
	port = 5555
	try: 
		s.bind((host,port))
	except socket.error as e:
		print(str(e))
	s.listen(5)
	con, addr = s.accept()

	print('connected to : ' + addr[0])

	def creatConnection(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host = ''
		port = 5555	

		try: 
			s.bind((host,port))
		except socket.error as e:
			print(str(e))

		s.listen(5)

def main():
	sTest = socketsTest()
	#s.creatConnection()


if __name__ == '__main__':
	main()