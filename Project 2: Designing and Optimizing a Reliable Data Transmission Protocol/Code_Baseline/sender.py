#!/usr/bin/env python3
from monitor import Monitor
import sys
import time
import os

# Config File
import configparser


import threading

def listener(send_monitor):

	while True:

		global msg_received, stop_thread, recv_time

		addr, recv_data = send_monitor.recv(max_packet_size)
		# print(f"thread - msg_received, {time.time()}")
		msg_received = True
		recv_time = time.time()

		if recv_data == b'[receiver] end':
			recv_time = time.time()
			# print("received: [receiver] end")
			return


msg_received = False


if __name__ == '__main__':
	print("Sender starting up!")
	config_path = sys.argv[1]

	# Initialize sender monitor
	send_monitor = Monitor(config_path, 'sender')
	
	# Parse config file
	cfg = configparser.RawConfigParser(allow_no_value=True)
	cfg.read(config_path)
	receiver_id = int(cfg.get('receiver', 'id'))
	file_to_send = cfg.get('nodes', 'file_to_send')
	max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))

	# Set timeout
	link_bw = int(cfg.get('network', 'LINK_BANDWIDTH'))
	prop_delay = float(cfg.get('network', 'PROP_DELAY'))
	timeout = max_packet_size / link_bw + prop_delay*2.1
	# print(f"{timeout = }")


	# Exchange messages!
	# print('Sender: Sending "Hello, World!" to receiver.')
	# send_monitor.send(receiver_id, b'Hello, World!')
	# addr, data = send_monitor.recv(max_packet_size)
	# print(f'Sender: Got response from id {addr}: {data}')

	th_listener = threading.Thread(target=listener, args=(send_monitor, ))
	th_listener.start()

	# Read file and send
	file_to_send = os.path.dirname(os.getcwd()) + file_to_send[2:]
	f = open(file_to_send,"rb")
	data = f.read(int(max_packet_size-4))
	send_monitor.send(receiver_id, data)
	# print(f"sending ... {len(datsa) = }")

	recv_time = time.time()

	while True:
		
		time.sleep(timeout)

		if msg_received:
			msg_received = False
			data = f.read(int(max_packet_size-4))
			if data:
				send_monitor.send(receiver_id, data)
				# print("sending ...", data[:10])
			else:
				break
			

		elif time.time() - recv_time > timeout:
			send_monitor.send(receiver_id, data)
			print("** resending ...", data[:10])


	f.close()

	send_monitor.send(receiver_id, b'[sender] end')
	# print("sent: [sender] end")

	time.sleep(timeout)

	# print(f"{recv_time = }, {time.time() = }, {time.time() - recv_time}")
	while time.time() - recv_time > timeout:
		send_monitor.send(receiver_id, b'[sender] end')
		print("resend: [sender] end")
		time.sleep(timeout)

	th_listener.join()
	send_monitor.send_end(receiver_id)
	# print("send_monitor.send_end")
	

	# Exit! Make sure the receiver ends before the sender. send_end will stop the emulator.
	# send_monitor.send_end(receiver_id)