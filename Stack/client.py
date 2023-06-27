import socket
import pickle

class Layer:
    def setPDU(self, data):
        self.PDU = data
        
    def encapsulate(self, data, header):
        packet = []
        packet.append("{} Header".format(header))
        packet.append(data)
        
        if header == 'Frame':
            packet.append("{} Footer".format(header))
        
        return packet


class Client:

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.MAX_TRANSFER_SIZE = 1024
    
    
    def setup(self):
        # Create a connection to the server application on port
        self.CONNECTION = socket.create_connection((self.HOST, self.PORT))
        
        print("Type 'help' to see the manual.\n")
    
    
    def awaitCommand(self):
        self.COMMAND = input("client@{}~> ".format(self.HOST))
    
    
    def help(self):
        print("\nOPTIONS")
        print("     help                See the manual.")
        print("     ping                Receive the server IP.")
        print("     handshake           Simulate a TCP handshake.")
        print("     stack               Simulate the TCP/IP encapsulation process.")
        print("     [ text ]            Send message to server.")
        print("     exit, [ empty ]     Quit the program.")
        print("")
        
        
    def ping(self):
        self.CONNECTION.sendall(self.COMMAND.encode())

        received = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE).decode()
        print("{}\n".format(received))
        
        
    def handshake(self):
        self.CONNECTION.sendall('SYN'.encode())
        print("'SYN' sent.")
        
        received1 = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE).decode()
        received2 = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE).decode()
        
        if received1 == 'SYN' and received2 == 'ACK':
            print("{} received.".format(received1))
            print("{} received.".format(received2))
            
            self.CONNECTION.sendall('ACK'.encode())
            print("'ACK' sent.\n")
        else:
            print("Error during Three Way Handshake.")
        
        
    def stack(self):
        message = input("Write your message: ")
        
        application = Layer()
        application.setPDU([message])
        data = application.PDU
        print("\nApplication Layer - Created Data:")
        print("{}\n".format(data))
        
        transport = Layer()
        transport.setPDU(transport.encapsulate(data, 'TCP'))
        segment = transport.PDU
        print("Transport Layer - Created Segment:")
        print("{}\n".format(segment))
        
        print("Establishing connection through a Three-Way Handshake...")
        self.handshake()
        
        network = Layer()
        network.setPDU(network.encapsulate(segment, 'IP'))
        packet = network.PDU
        print("Network Layer - Created Packet:")
        print("{}\n".format(packet))
        
        netInterface = Layer()
        netInterface.setPDU(netInterface.encapsulate(packet, 'Frame'))
        frame = netInterface.PDU
        print("Network Interface Layer - Created Frame (Frame Footer implied):")
        print("{}\n".format(frame))
        
        self.CONNECTION.sendall(pickle.dumps(frame))
        print("Frame sent.\n")
        
        
    def sendMsg(self):
        self.CONNECTION.sendall(self.COMMAND.encode())
    
    
    def closeSocket(self):
        print("Closing socket...")
        self.CONNECTION.close()
        print("Quitting the program...")
    
    
client = Client('localhost', 3333)
client.setup()

try:
    while True:

        client.awaitCommand()

        if not client.COMMAND:
            break

        if client.COMMAND == 'help':
            client.help()

        elif client.COMMAND == 'ping':
            client.ping()

        elif client.COMMAND == 'handshake':
            client.handshake()
            
        elif client.COMMAND == 'stack':
            client.stack()
        
        elif client.COMMAND == 'exit':
            break
        
        else:
            client.sendMsg()
        
finally:
    client.closeSocket()

