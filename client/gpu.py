class GPU:
   'Common base class for all gpu\'s'
   totalGPUs = 0

   def __init__(self):
      self.index = None
      self.name = None
      self.display = None
      self.engine = None
      self.memory = None
      self.volts = None
      self.performance = None
      self.utilization = None
      self.fan = None
      self.fanRMP = None
      self.temp = None
      self.power = None
      self.JSON = ''


      GPU.totalGPUs += 1
   
   def getTotal(self):
      return GPU.totalGPUs

   def setObject(self):
      self.JSON = "{index: \""+str(self.index)+"\", name: \""+self.name+"\", display: \""+self.display+"\", engine:\""+str(self.engine)+"\", memory: \""+str(self.memory)+"\", volts:\""+str(self.volts)+"\", performance: \""+str(self.performance)+"\", utilization:\""+str(self.utilization)+"\", fan: \""+str(self.fan)+"\", temp:\""+str(self.temp)+"\", power: \""+str(self.power)+"\"}"

   def printGPU(self):
      print self.JSON

   def printCleanGPU(self):
      print "index: "+str(self.index)+", name: "+self.name+", display: "+self.display+"\nengine:"+str(self.engine)+", memory: "+str(self.memory)+", volts:"+str(self.volts)+"\nperformance: "+str(self.performance)+", utilization:"+str(self.utilization)+", fan: "+str(self.fan)+", temp:"+str(self.temp)+", power: "+str(self.power)+"\n"