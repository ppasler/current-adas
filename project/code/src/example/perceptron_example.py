
# Code from Chapter 3 of Machine Learning: An Algorithmic Perspective (2nd Edition)
# by Stephen Marsland (http://stephenmonika.net)

# You are free to use, change, or redistribute the code in any way you wish for
# non-commercial purposes, but please maintain the name of the original author.
# This code comes with no warranty of any kind.

# Stephen Marsland, 2008, 2014

import numpy as np

class pcn(object):
	""" A basic Perceptron"""
	
	def __init__(self,inputs,targets):
		""" Constructor """
		# Set up network size
		if np.ndim(inputs)>1:
			self.nIn = np.shape(inputs)[1]
		else: 
			self.nIn = 1
	
		if np.ndim(targets)>1:
			self.nOut = np.shape(targets)[1]
		else:
			self.nOut = 1

		self.nData = np.shape(inputs)[0]
	
		# Initialise network
		self.weights = np.random.rand(self.nIn+1,self.nOut)*0.1-0.05


	def pcntrain(self,inputs,targets,eta,nIterations):
		""" Train the thing """	
		# Add the inputs that match the bias node
		inputs = np.concatenate((inputs,-np.ones((self.nData,1))),axis=1)
		# Training
		for _ in range(nIterations):
			#print "Iteration %d" % n
			self.activations = self.pcnfwd(inputs);
			self.weights -= eta*np.dot(np.transpose(inputs),self.activations-targets)
			#print self.weights
			# Randomise order of inputs
			inputs, targets = shuffle(inputs, targets)
			
		#return self.weights

	def pcnfwd(self,inputs):
		""" Run the network forward """
		# Compute activations
		activations =  np.dot(inputs,self.weights)

		# Threshold the activations
		return np.where(activations>0,1,0)


	def confmat(self,inputs,targets):
		"""Confusion matrix"""

		# Add the inputs that match the bias node
		inputs = np.concatenate((inputs,-np.ones((self.nData,1))),axis=1)
		
		outputs = np.dot(inputs,self.weights)
	
		nClasses = np.shape(targets)[1]

		if nClasses==1:
			nClasses = 2
			outputs = np.where(outputs>0,1,0)
		else:
			# 1-of-N encoding
			outputs = np.argmax(outputs,1)
			targets = np.argmax(targets,1)

		cm = np.zeros((nClasses,nClasses))
		for i in range(nClasses):
			for j in range(nClasses):
				cm[i,j] = np.sum(np.where(outputs==i,1,0)*np.where(targets==j,1,0))

		return cm, np.trace(cm)/np.sum(cm)

def shuffle(inputs, targets):
	nData = np.shape(inputs)[0]
	change = range(nData)

	np.random.shuffle(change)
	return inputs[change,:], targets[change,:]

def separateData(data):
	return data[:,0:2],data[:,2:]

def printInfo(funcName, inputs, targets):
	print "Running %s function\nInputs:\n %s\nTargets:\n%s" % (funcName, inputs, targets)

def printResult(confmat, rights):
	print "Rights %d%%\nConfmat\n%s" % (rights*100, confmat) 

def xorFunction():
	""" Run AND and XOR logic functions"""
	data = np.array([[0,0,0],[0,1,1],[1,0,1],[1,1,0]])
	inputs, targets = separateData(data)
	
	printInfo("XOR", inputs, targets)
	
	p = pcn(inputs, targets)
	p.pcntrain(inputs, targets, 0.25, 10)
	
	inputs, targets = shuffle(inputs, targets)
	confmat, rights = p.confmat(inputs, targets)
	printResult(confmat, rights)

def andFunction():
	data = np.array([[0,0,0],[0,1,0],[1,0,0],[1,1,1]])
	inputs, targets = separateData(data)
	
	printInfo("AND", inputs, targets)
	
	p = pcn(inputs, targets)
	p.pcntrain(inputs, targets, 0.25, 10)
	
	inputs, targets = shuffle(inputs, targets)
	confmat, rights = p.confmat(inputs, targets)
	printResult(confmat, rights)

def orFunction():
	data = np.array([[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
	inputs, targets = separateData(data)
	
	printInfo("AND", inputs, targets)
	
	p = pcn(inputs, targets)
	p.pcntrain(inputs, targets, 0.25, 10)
	
	inputs, targets = shuffle(inputs, targets)
	confmat, rights = p.confmat(inputs, targets)
	printResult(confmat, rights)

if __name__ == "__main__":
	#logic()
	andFunction()
	orFunction()
	xorFunction()

	