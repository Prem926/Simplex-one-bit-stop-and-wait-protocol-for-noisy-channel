import socket
import time
import random
import threading

# Sender (Client) class implementing Stop-and-Wait ARQ
class StopAndWaitSender:
    def __init__(self, host='localhost', port=5000, timeout=5, debug=True):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.seq_num = 0
        self.debug = debug
        self.stats = {"success": 0, "retransmissions": 0, "errors": 0}

    def checksum(self, data):
        return sum(data) % 256

    def simulate_error(self, data):
        if random.random() < 0.2:  # 20% chance of data corruption or loss
            if self.debug:
                print("[ERROR] Simulating data corruption.")
            return bytearray(random.getrandbits(8) for _ in data)
        return data

    def send_message(self, message):
        message_bytes = bytearray(message, 'utf-8')
        packet = bytearray([self.seq_num]) + message_bytes
        packet.append(self.checksum(packet))

        while True:
            corrupted_packet = self.simulate_error(packet)
            self.sock.sendto(corrupted_packet, (self.host, self.port))
            if self.debug:
                print(f"[INFO] Sent frame with sequence number {self.seq_num}")

            try:
                ack, _ = self.sock.recvfrom(1024)
                ack_seq_num, = ack
                if ack_seq_num == self.seq_num:
                    print(f"[SUCCESS] ACK received for sequence number {self.seq_num}")
                    self.stats["success"] += 1
                    self.seq_num = 1 - self.seq_num  # Toggle sequence number
                    break
                else:
                    print(f"[WARNING] Duplicate ACK for sequence {ack_seq_num}")
            except socket.timeout:
                print("[TIMEOUT] No ACK received, retransmitting...")
                self.stats["retransmissions"] += 1

    def close(self):
        self.sock.close()
        print("[INFO] Connection closed.")
        print("[STATS] Successful transmissions:", self.stats["success"])
        print("[STATS] Retransmissions:", self.stats["retransmissions"])
        print("[STATS] Errors:", self.stats["errors"])

if __name__ == "__main__":
    sender = StopAndWaitSender(debug=True)
    messages = ["Hello", "Stop and Wait", "Protocol", "Testing", "Goodbye"]

    for msg in messages:
        sender.send_message(msg)
        time.sleep(1)

    sender.close()  