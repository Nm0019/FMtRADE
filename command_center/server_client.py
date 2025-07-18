# network/server_client.py

import socket
import json


class SignalClient:
    def __init__(self, server_ip="192.168.1.184", port=14021):
        self.server_ip = server_ip
        self.port = port
        self.sock = None

    def connect(self):
        """اتصال به سرور"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip, self.port))
            print(f"✅ Connected to server at {self.server_ip}:{self.port}")
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            self.sock = None

    def send_signal(self, signal_type: str, symbol: str):
        """
        ارسال سیگنال به سرور به صورت JSON
        (تک پیام - در صورت نیاز می‌توان غیرفعال کرد)
        """
        if not self.sock:
            print("⚠️ Not connected to server. Cannot send signal.")
            return

        try:
            message = json.dumps({"symbol": symbol, "signal": signal_type}) + "\n"
            self.sock.sendall(message.encode("utf-8"))
            print(f"📤 Sent to server: {message.strip()}")
        except Exception as e:
            print(f"❌ Error sending signal: {e}")

    def send_signals_batch(self, signals: list):
        """
        ارسال گروهی سیگنال‌ها به صورت یک آرایه JSON
        Example:
            [{"symbol": "BTCUSD", "signal": "BUY"}, {"symbol": "ETHUSD", "signal": "SELL"}]
        """
        if not self.sock:
            print("⚠️ Not connected to server. Cannot send batch.")
            return

        try:
            message = json.dumps(signals) + "\n"
            self.sock.sendall(message.encode("utf-8"))
            print(f"📤 Sent batch to server ({len(signals)} signals)")
        except Exception as e:
            print(f"❌ Error sending signal batch: {e}")

    def send_exit(self):
        """ارسال پیام خروج به سرور"""
        if self.sock:
            try:
                self.sock.sendall("EXIT\n".encode("utf-8"))
                print("📤 Sent: EXIT")
            except:
                pass

    def close(self):
        """بستن اتصال"""
        if self.sock:
            try:
                self.sock.close()
                print("🔌 Connection closed.")
            except:
                pass
            self.sock = None
