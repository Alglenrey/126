"""
Food Ordering System Simulation using OSI Model (Real IP and MAC Addresses)

This Python program simulates a realistic food ordering process using a layered architecture
based on the OSI model. It dynamically integrates the actual local IP address and MAC address
of the user's laptop to closely resemble real network communication. Due to sandbox constraints,
it uses an internal queue instead of real network sockets and threading.

Layers Implemented:
1. Physical Layer - Simulates data transmission using an internal queue.
2. Data Link Layer - Dynamically retrieves and incorporates the laptop's real MAC address.
3. Network Layer - Dynamically retrieves and uses the laptop's actual local IP address for realistic packet headers.
4. Transport Layer - Adds sequencing headers to ensure ordered data transmission.
5. Session Layer - Manages session states for client-server communication.
6. Presentation Layer - Handles Base64 encoding and decoding of messages.
7. Application Layer - Implements a simplified request-response system for placing food orders.

How it Works:
- A customer places an order at the Application Layer.
- The order moves through the layers, receiving realistic MAC and IP addresses, sequencing, encoding, and framing.
- The Physical Layer transmits the order via the mocked queue.
- The server-side response (confirmation) travels back up through the layers to the Application Layer.
- The Application Layer displays the confirmation message.

Constraints Met:
- No external networking libraries.
- Uses only standard Python libraries.
- Fully simulates OSI communication with real network identifiers without actual sockets or threads.

Run the program to simulate an order from "Al Glenrey" ordering "Pizza."
"""

import queue
import base64
import json
import time
import socket
import uuid

def print_layer(layer_name, message):
    print(f"[{layer_name}] {message}\n")

class MockNetwork:
    def __init__(self):
        self.queue = queue.Queue()

    def send(self, data):
        print_layer("Physical Layer", f"⬇️ Sending data:\n{data}")
        self.queue.put(data)

    def receive(self):
        data = self.queue.get()
        print_layer("Physical Layer", f"⬆️ Received data:\n{data}")
        return data

class PhysicalLayer:
    def __init__(self, network):
        self.network = network
        print_layer("Physical Layer", "✅ Initialized")

    def send(self, data):
        self.network.send(data)

    def receive(self):
        return self.network.receive()

class DataLinkLayer:
    def __init__(self, physical_layer):
        self.physical_layer = physical_layer
        self.mac_address = self.get_mac_address()
        print_layer("Data Link Layer", f"✅ Initialized with MAC: {self.mac_address}")

    def get_mac_address(self):
        mac = uuid.getnode()
        mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        return mac_str

    def send(self, data):
        frame = f"{self.mac_address}|{data}"
        print_layer("Data Link Layer", f"📦 Framing data:\n{frame}")
        self.physical_layer.send(frame)

    def receive(self):
        data = self.physical_layer.receive()
        return data.split("|", 1)[1] if "|" in data else data

class NetworkLayer:
    def __init__(self, data_link_layer):
        self.data_link_layer = data_link_layer
        self.source_ip = self.get_my_ip()
        self.destination_ip = "192.168.1.100"
        print_layer("Network Layer", f"✅ Initialized with IP: {self.source_ip} → {self.destination_ip}")

    def get_my_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            my_ip = s.getsockname()[0]
        except:
            my_ip = '127.0.0.1'
        finally:
            s.close()
        return my_ip

    def send(self, data):
        packet = f"{self.source_ip}>{self.destination_ip}|{data}"
        print_layer("Network Layer", f"🌍 Routing packet:\n{packet}")
        self.data_link_layer.send(packet)

    def receive(self):
        data = self.data_link_layer.receive()
        if "|" in data:
            ip_info, payload = data.split("|", 1)
            print_layer("Network Layer", f"📍 Packet info: {ip_info}")
            return payload
        return data

class TransportLayer:
    def __init__(self, network_layer):
        self.network_layer = network_layer
        print_layer("Transport Layer", "✅ Initialized")

    def send(self, data):
        segment = f"SEQ_HEADER|{data}"
        print_layer("Transport Layer", f"📜 Adding sequencing:\n{segment}")
        self.network_layer.send(segment)

    def receive(self):
        data = self.network_layer.receive()
        return data.split("|", 1)[1] if "|" in data else data

class SessionLayer:
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.session_active = False
        print_layer("Session Layer", "✅ Initialized")

    def start_session(self):
        self.session_active = True
        print_layer("Session Layer", "🔄 Session started")

    def send(self, data):
        if self.session_active:
            self.transport_layer.send(data)

    def receive(self):
        if self.session_active:
            return self.transport_layer.receive()

class PresentationLayer:
    def __init__(self, session_layer):
        self.session_layer = session_layer
        print_layer("Presentation Layer", "✅ Initialized")

    def send(self, data):
        encoded_data = base64.b64encode(data.encode()).decode()
        print_layer("Presentation Layer", f"🔐 Encoding data:\n{encoded_data}")
        self.session_layer.send(encoded_data)

    def receive(self):
        data = self.session_layer.receive()
        if data.startswith("CONFIRMATION|"):
            return data.split("|", 1)[1]
        decoded_data = base64.b64decode(data).decode()
        print_layer("Presentation Layer", f"🔓 Decoded data:\n{decoded_data}")
        return decoded_data

class ApplicationLayer:
    def __init__(self, presentation_layer):
        self.presentation_layer = presentation_layer
        print_layer("Application Layer", "✅ Initialized")

    def place_order(self, customer, food, quantity, address):
        order = json.dumps({
            "customer": customer,
            "food": food,
            "quantity": quantity,
            "address": address
        }, indent=4)
        print_layer("Application Layer", f"🛒 Placing order:\n{order}")
        self.presentation_layer.send(order)

    def receive_confirmation(self):
        confirmation = self.presentation_layer.receive()
        if confirmation:
            print_layer("Application Layer", f"✅ Order confirmed:\n{confirmation}")

if __name__ == "__main__":
    print("\n=================== 🍽️ Starting Food Ordering System (Mocked Network) ===================\n")

    network = MockNetwork()
    physical = PhysicalLayer(network)
    data_link = DataLinkLayer(physical)
    network_layer = NetworkLayer(data_link)
    transport = TransportLayer(network_layer)
    session = SessionLayer(transport)
    presentation = PresentationLayer(session)
    application = ApplicationLayer(presentation)

    session.start_session()
    application.place_order("Al Glenrey", "Pizza", 2, "University of the Philippines Cebu, Lahug, Cebu City")
    time.sleep(1)

    # Simulate confirmation coming from server (for demo purposes)
    encoded_confirmation = base64.b64encode("CONFIRMATION|Order received, preparing Pizza!".encode()).decode()
    network.send(f"SERVER_MAC|192.168.1.100>{network_layer.source_ip}|SEQ_HEADER|{encoded_confirmation}")

    application.receive_confirmation()

    print("\n===================  Simulation Complete ===================")

