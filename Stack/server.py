import socket
import pickle

class Layer:

    def __init__(self, data):
        self.PDU = data
        
        
    def decapsulate(self, packet):
        data = packet.pop()
        return data


class Server:

    def __init__(self, host, port):
        # Initial server variables
        self.HOST = host
        self.PORT = port
        self.MAX_TRANSFER_SIZE = 1024
    
    
    def setup(self):
        # Set up a TCP/IP server
        self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Bind the socket to server address and port
        hook = (self.HOST, self.PORT)
        self.TCP.bind(hook)

        # Listen on port
        self.TCP.listen(1)
        
        
    def awaitConnection(self):
        print("Waiting for connection...")
        self.CONNECTION, client = self.TCP.accept()
        
        print("Connected to client IP: {}".format(client))
    
    
    def awaitMessage(self):
        # Receive and print data a few bytes at a time, as long as the client is sending something
        self.MESSAGE = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE)
        
        # Try to decode received message, if it fails, it is bytes-type data
        try:
            self.MESSAGE = self.MESSAGE.decode()
        except (UnicodeDecodeError, AttributeError):
            self.MESSAGE = pickle.loads(self.MESSAGE)
    
    
    def ping(self):
        print("{} request received.\n".format(self.MESSAGE))
        self.CONNECTION.sendall(self.HOST.encode())
        
        
    def handshake(self):
        print("{} request received.".format(self.MESSAGE))
        
        self.CONNECTION.sendall('SYN'.encode())
        print("'SYN' sent.")
        
        self.CONNECTION.sendall('ACK'.encode())
        print("'ACK' sent.")
        
        
    def stack(self):
        netInterface = Layer(self.MESSAGE)
        frame = netInterface.PDU
        print("Frame received:")
        print("{}\n".format(frame))
        
        network = Layer(netInterface.decapsulate(frame))
        packet = network.PDU
        print("Network Interface Layer - Processed Frame Header:")
        print("{}\n".format(packet))
        packet = network.decapsulate(frame[:-1])
        
        transport = Layer(network.decapsulate(packet))
        segment = transport.PDU
        print("Network Layer - Processed Packet Header:")
        print("{}\n".format(segment))
        
        application = Layer(transport.decapsulate(segment))
        data = application.PDU
        print("Transport Layer - Processed Segment Header:")
        print("{}\n".format(data))
        
        message = application.decapsulate(data)
        print("Application Layer - Processed Data:")
        print("{}\n".format(message))
        
        print("Message Received: {}\n".format(message))
        
        
    def printMsg(self):
        print("Received: {}\n".format(self.MESSAGE))
    
    
    def closeSocket(self):
        print("Closing socket...")
        self.CONNECTION.close()
        print("Quitting the program...")


server = Server('127.0.0.1', 3333)
server.setup()
server.awaitConnection()

try:     
    while True:
    
        server.awaitMessage()
        
        if not server.MESSAGE:
            break
        
        if server.MESSAGE == 'ping':
            server.ping()
            
        elif server.MESSAGE == 'SYN':
            server.handshake()
            
        elif isinstance(server.MESSAGE, list) == True:
            server.stack()
        
        else:
            server.printMsg()

finally:
    server.closeSocket()

