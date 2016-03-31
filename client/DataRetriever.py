from gpu import GPU
from all_params import *


class DataRetriever:
	
	def __init__(self):
		self.data = None
		self.size = 0
		self.updated = 0

		try:
		  initialize()
		  adapter_list = None
		  self.data = show_status(adapter_list=adapter_list)
		  self.size = len(self.data)

		  result = 0
		  temp_gpu = GPU()

		except ADLError, err:
		  result = 1
		  print err
		        
		finally:        
		  shutdown()

	def getSize(self):
		return self.size

	def getData(self):

		try:
			initialize()
			adapter_list = None
			self.data = show_status(adapter_list=adapter_list)

			result = 0
			return self.data

		except ADLError, err:
		  result = 1
		  print err
		        
		finally:        
		  shutdown()

				



