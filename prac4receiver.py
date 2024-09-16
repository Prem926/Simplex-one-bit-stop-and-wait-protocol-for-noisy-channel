import socket
import random

class StopAndWaitReceiver:
    def __init__(self, host='localhost', port=5000, debug=True):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.expected_seq_num = 0
        self.debug = debug

    def checksum(self, data):
        return sum(data) % 256

    def is_corrupt(self, packet):
        received_checksum = packet[-1]
        data_checksum = self.checksum(packet[:-1])
        return received_checksum != data_checksum

    def simulate_ack_loss(self):
        return random.random() < 0.1  # 10% chance of ACK loss

    def start(self):
        print("[INFO] Receiver is ready to receive messages.")
        while True:
            try:
                packet, addr = self.sock.recvfrom(1024)
                seq_num = packet[0]

                if self.is_corrupt(packet):
                    print("[ERROR] Packet corrupted. Waiting for retransmission.")
                    continue

                if seq_num == self.expected_seq_num:
                    message = packet[1:-1].decode('utf-8')
                    print(f"[RECEIVED] Message: {message} (Seq: {seq_num})")
                    self.expected_seq_num = 1 - self.expected_seq_num
                else:
                    print(f"[WARNING] Duplicate packet received (Seq: {seq_num}). Ignoring.")

                # Send ACK if not lost
                if not self.simulate_ack_loss():
                    ack_packet = bytearray([seq_num])
                    self.sock.sendto(ack_packet, addr)
                    if self.debug:
                        print(f"[INFO] ACK sent for sequence number {seq_num}")
                else:
                    if self.debug:
                        print("[ERROR] Simulating ACK loss.")

            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")
                continue

if __name__ == "__main__":
    receiver = StopAndWaitReceiver(debug=True)
    receiver.start()
