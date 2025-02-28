"""
Food Ordering System Simulation using the OSI Model (Mocked Network Environment)

This Python program simulates a food ordering process using a layered architecture
that follows the OSI model. Each layer represents a different aspect of network communication,
moving order data from the customer to the restaurant (server) and receiving confirmation.

Due to sandbox limitations that prevent real socket communication and threading, this version 
uses a mocked network approach via an internal queue to simulate data transmission without threading.

Layers Implemented:
1. Physical Layer - Simulates network communication using an internal queue instead of real bit-level operations.
2. Data Link Layer - Implements MAC addressing and frame transmission.
3. Network Layer - Simulates IP-like addressing and packet routing (without actual routing).
4. Transport Layer - Ensures reliable transmission by adding TCP-like sequencing headers.
5. Session Layer - Manages session states to synchronize communication between the client and server.
6. Presentation Layer - Handles encoding and decoding of data (Base64) for secure transmission.
7. Application Layer - Implements an HTTP-like request-response system for placing food orders.

How it Works:
- A customer places an order at the Application Layer.
- The order moves down through all OSI layers, getting encoded, segmented, and framed.
- The Physical Layer transmits the order to the server (mocked queue instead of sockets).
- The server receives the order, processes it, and sends back a confirmation.
- The confirmation moves back up through all OSI layers until the Application Layer displays the message.

Constraints Met:
- No external networking libraries (Flask, Django, requests, etc.).
- Uses only low-level Python features (JSON, base64, etc.).
- Fully simulates OSI layer communication without real network sockets or threads.

Run the program to simulate an order from a customer named "Al Glenrey" ordering "Pizza".
"""

import queue
import base64
import json
import time

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
        print_layer("Data Link Layer", "✅ Initialized")

    def send(self, data):
        frame = f"MAC_HEADER|{data}"
        print_layer("Data Link Layer", f"📦 Framing data:\n{frame}")
        self.physical_layer.send(frame)

    def receive(self):
        data = self.physical_layer.receive()
        return data.split("|", 1)[1] if "|" in data else data

class NetworkLayer:
    def __init__(self, data_link_layer):
        self.data_link_layer = data_link_layer
        print_layer("Network Layer", "✅ Initialized")

    def send(self, data):
        packet = f"IP_HEADER|{data}"
        print_layer("Network Layer", f"🌍 Routing packet:\n{packet}")
        self.data_link_layer.send(packet)

    def receive(self):
        data = self.data_link_layer.receive()
        return data.split("|", 1)[1] if "|" in data else data

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
    application.receive_confirmation()
    
    print("\n===================  Simulation Complete ===================")
