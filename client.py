
import cv2, imutils, socket
import numpy as np
import time, os
import base64
import threading, wave, pyaudio,pickle,struct
BUFF_SIZE = 65536

BREAK = False
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '196.109.118.204'
#host_ip socket.gethostbyname(host_name)
port = 9688
message = b'Hello'
print(f"{host_ip} on {port}")
client_socket.sendto(message,(host_ip,port))

def video_stream():
	
	cv2.namedWindow('RECEIVING VIDEO')        
	cv2.moveWindow('RECEIVING VIDEO', 10,360) 
	fps,st,frames_to_count,cnt = (0,0,20,0)
	while True:
		packet,_ = client_socket.recvfrom(BUFF_SIZE)
		data = base64.b64decode(packet,' /')
		npdata = np.frombuffer(data,dtype=np.uint8)
		# npdata = np.fromstring(data,dtype=np.uint8)
	
		frame = cv2.imdecode(npdata,1)
		cv2.imshow("RECEIVING VIDEO",frame)
		key = cv2.waitKey(1) & 0xFF
	
		if key == ord('q'):
			client_socket.close()
			os._exit(1)
			break

		if cnt == frames_to_count:
			try:
				fps = round(frames_to_count/(time.time()-st))
				st=time.time()
				cnt=0
			except:
				pass
		cnt+=1
	
	client_socket.close()
	cv2.destroyAllWindows() 


def audio_stream():
	
	p = pyaudio.PyAudio()
	CHUNK = 1024
	stream = p.open(format=p.get_format_from_width(2),
					channels=2,
					rate=44100,
					output=True,
					frames_per_buffer=CHUNK)
					
	# create socket
	client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	socket_address = (host_ip,port-1)
	print('server listening at',socket_address)
	client_socket.connect(socket_address) 
	print("CLIENT CONNECTED TO",socket_address)
	data = b""
	payload_size = struct.calcsize("Q")
	while True:
		try:
			while len(data) < payload_size:
				packet = client_socket.recv(4*1024) # 4K
				if not packet: break
				data+=packet
			packed_msg_size = data[:payload_size]
			data = data[payload_size:]
			msg_size = struct.unpack("Q",packed_msg_size)[0]
			while len(data) < msg_size:
				data += client_socket.recv(4*1024)
			frame_data = data[:msg_size]
			data  = data[msg_size:]
			frame = pickle.loads(frame_data)
			stream.write(frame)

		except:
			
			break

	client_socket.close()
	print('Audio closed',BREAK)
	os._exit(1)
	


from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=2) as executor:
	# executor.submit(audio_stream) #to hear audio uncomment
	executor.submit(video_stream)























# import socket
# import io
# import time

# # create socket object
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # Get the message size
# message_size = s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
# print(message_size.decode())
# # get local machine name
# host =socket.gethostbyname(socket.gethostname())

# port = 10021

# # connection to hostname on the port
# s.connect((host, port))

# # receive no more than 1024 bytes
# while True:
#     msg = s.recv(21383097)

#     buffer_reader = io.BufferedReader(io.BytesIO(msg))
#     print(type(buffer_reader))
#     with open('file.png','wb') as file:
#         file.write(buffer_reader.read())
#         time.sleep(100)
#     # s.close()
