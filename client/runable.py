from gpu import GPU
from sender import Sender
from DataRetriever import DataRetriever


host = raw_input("Enter host IP: ")
port = raw_input("Enter host port number: ")
name = raw_input("Enter the name of this machine: ")

sender = Sender(host, port, name)