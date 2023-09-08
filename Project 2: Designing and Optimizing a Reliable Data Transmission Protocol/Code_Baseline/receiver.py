#!/usr/bin/env python3
from monitor import Monitor
import sys
import time

# Config File
import configparser

if __name__ == '__main__':
	print("Receivier starting up!")
	config_path = sys.argv[1]

	# Initialize sender monitor
	recv_monitor = Monitor(config_path, 'receiver')
	
	# Parse config file
	cfg = configparser.RawConfigParser(allow_no_value=True)
	cfg.read(config_path)
	sender_id = int(cfg.get('sender', 'id'))
	file_to_send = cfg.get('nodes', 'file_to_send')
	max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))

	# Set timeout
	link_bw = int(cfg.get('network', 'LINK_BANDWIDTH'))
	prop_delay = float(cfg.get('network', 'PROP_DELAY'))
	timeout = max_packet_size / link_bw + prop_delay
	# print(f"{timeout = }")

	# Exchange messages!
	# addr, data = recv_monitor.recv(max_packet_size)
	# print(f'Receiver: Got message from id {addr}: {data}')
	# print('Receiver: Responding with "Hello, Sender!".')
	# recv_monitor.send(sender_id, b'Hello, Sender!')

	# Receive data
	data_old = b' '
	f_recv_bytes = b''
	ack_str = b' '*(max_packet_size)

	while True:
		addr, data_new = recv_monitor.recv(max_packet_size)
		# print("Received --> ", data_new[:10])

		if data_new != b'[sender] end':
			recv_monitor.send(sender_id, ack_str)
			if data_new != data_old:
				f_recv_bytes += data_new
			# addr, data = recv_monitor.recv(max_packet_size)
			# print(f"ack sent, {data_new[:10] = }, {len(data_new) = }, {time.time()}")
			data_old = data_new
			# time.sleep(timeout)
		else:
			# print(f"{data_new}, {len(data_new) = }, {time.time()}")
			break
	
	f_recv = open('received_file.txt','w')
	f_recv.write(f_recv_bytes.decode('utf-8'))
	f_recv.close()
	print("File Downloaded")
	recv_monitor.send(sender_id, b'[receiver] end')
	recv_monitor.send(sender_id, b'[receiver] end')
	recv_monitor.send(sender_id, b'[receiver] end')
	# print("[receiver] end sent")
	recv_monitor.recv_end('received_file.txt', sender_id)


	# Exit! Make sure the receiver ends before the sender. send_end will stop the emulator.
	# recv_monitor.recv_end('received_file', sender_id)