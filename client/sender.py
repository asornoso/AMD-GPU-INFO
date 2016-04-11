from Tkinter import *
from gpu import GPU
from DataRetriever import DataRetriever
from socketIO_client import SocketIO

class Sender:

	def __init__(self, host, port, machine):
		self.root = Tk()
		self.retriever = DataRetriever()

		self.host = host
		self.port = int(port)
		self.machine = machine

		self.socket = SocketIO(self.host, self.port)
		

		self.size = self.retriever.getSize()

		if self.size > 0:
			self.gpus = None
			self.engLabels = [-1] * self.size
			self.memLabels = [-1] * self.size
			self.fanLabels = [-1] * self.size
			self.utilLabels = [-1] * self.size
			self.tempLabels = [-1] * self.size
			self.voltsLabels = [-1] * self.size

			self.sections = [-1] * self.size

			self.name = [-1] * self.size
			self.machines = [-1] * self.size

			self.firstTime = [True] * self.size
			
			# self.parse(self.retriever.getData())


			self.callData()

			self.display()
		else:
			print('No AMD gpu\'s found: '+ str(self.size))


	def callData(self):
		self.parse(self.retriever.getData())
		self.root.after(7000, self.callData)

	def parse(self, data):
		for gpu in data:
			self.receive(gpu)

	def receive(self, gpu):
		if gpu != -1 and gpu.index < len(self.size):
			if self.firstTime[gpu.index]:
				self.createFrame(gpu)
				self.firstTime[gpu.index] = False;
			else:
				self.updateFrame(gpu)

			self.sendData(gpu)
		else:
			print "ERROR: EMPTY OR NO GPU'S FOUND!!!!"

	def createFrame(self, gpu):

		

		self.sections[gpu.index] = Frame(self.root, width=1200, height=200, bg='white', borderwidth=5) 
		
		title = Label(self.sections[gpu.index], text=gpu.name, bg='white')
		title.grid(row=0)

		self.engLabels[gpu.index] = Label(self.sections[gpu.index], text="ENGINGE CLOCK: "+str(gpu.engine)+"MHz")
		self.memLabels[gpu.index] = Label(self.sections[gpu.index], text="MEMORY CLOCK: "+str(gpu.memory)+"MHz")
		self.fanLabels[gpu.index] = Label(self.sections[gpu.index], text="FAN SPEED: "+str(gpu.fan)+"%")
		self.utilLabels[gpu.index] =  Label(self.sections[gpu.index], text="UTILIZATION: "+str(gpu.utilization)+"%")
		self.tempLabels[gpu.index] = Label(self.sections[gpu.index], text="TEMPERATURE: "+str(gpu.temp)+"C")
		self.voltsLabels[gpu.index] = Label(self.sections[gpu.index], text="VOLTS: "+str(gpu.volts))

		self.engLabels[gpu.index].grid(row=1, column=0)
		self.memLabels[gpu.index].grid(row=1, column=1)
		self.fanLabels[gpu.index].grid(row=1, column=2)
		self.utilLabels[gpu.index].grid(row=1, column=3)
		self.tempLabels[gpu.index].grid(row=1, column=4)
		self.voltsLabels[gpu.index].grid(row=1, column = 5)
		self.sections[gpu.index].grid(row=gpu.index, sticky=W)


	def display(self):
		self.root.wm_title("AMD GPU VISUALIZER")
		self.root.mainloop()

	def updateFrame(self, gpu):
		if self.engLabels[gpu.index] != -1 :
			self.engLabels[gpu.index].configure(text ="ENGINGE CLOCK: "+str(gpu.engine)+"MHz")
			self.memLabels[gpu.index].configure(text="MEMORY CLOCK: "+str(gpu.memory)+"MHz")
			self.fanLabels[gpu.index].configure(text="FAN SPEED: "+str(gpu.fan)+"%")
			self.utilLabels[gpu.index].configure(text="UTILIZATION: "+str(gpu.utilization)+"%")
			self.tempLabels[gpu.index].configure(text="TEMPERATURE: "+str(gpu.temp)+"C")
			self.voltsLabels[gpu.index].configure( text="VOLTS: "+str(gpu.volts))
		else:
			print('Updating Frame, but no labels for this gpu exist')

	def sendData(self, gpu):
		data = '{"machine":"'+self.machine+'", "name":"'+str(gpu.name)+'", "temp":"'+str(gpu.temp)+'", "util":"'+str(gpu.utilization)+'", "fan":"'+str(gpu.fan)+'", "volts":"'+str(gpu.volts)+'", "eng":"'+str(gpu.engine)+'", "mem":"'+str(gpu.memory)+'", "index":"'+str(gpu.index)+'"}'
		self.socket.emit('gpu_data', data)
		print "send!"
		
