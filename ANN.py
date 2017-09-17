import numpy as np
import os
import pickle

class BasicNeuralNetwork():
	def __init__(self, filepath=None):
		self.dim = [5, 4, 2]		# layer dimensions
		self.L = len(self.dim)		# no. of layers
		self.theta = []				# weights
		self.lambda_reg = 0.05	    # regularization factor
		self.learning_rate = 0.01   # learning factor
		self.filepath = filepath	# file path to save weights

		self.initWeights()
		self.sigmoid = np.vectorize(self.sigmoid)

	def initWeights(self):
		"""Initialize weights for each layer."""
		if self.filepath is None or not os.path.isfile(self.filepath):
			for cnt in range(self.L-1):
				self.theta.append((np.random.rand(self.dim[cnt+1], self.dim[cnt]+1)-0.5)*5)
		else:
			self.theta = pickle.load(open(self.filepath, 'rb'))

	def sigmoid(self, z):
		"""Apply sigmoid function."""
		return 1/(1+np.exp(-z))

	def forwardPropOne(self, x):
		"""Return the values of each post-activation layer."""
		x = np.array(x)
		a = [x]
		for cnt in range(self.L-1):
			x = self.sigmoid(np.dot(self.theta[cnt],np.insert(x,0,1,axis=0)))
			a.append(x)
		return a

	def predict(self, x):
		"""Return prediction for a single input vector."""
		x = np.array(x)
		for cnt in range(self.L-1):
			x = self.sigmoid(np.dot(self.theta[cnt], np.insert(x, 0, 1, axis=0)))
		return np.argmax(x)

	def backwardProp(self, a, y):
		"""Return weight update gradient."""
		y = np.array(y)
		sens = [a[-1]-y] # sensitivities of the cost function to each pre-activation value
						# initialized with the last layer sensitivity of output - expected
		# Calculate sensitivities for each layer
		for cnt in range(self.L-2, 0, -1):
			sens.insert(0, np.multiply(np.dot(self.theta[cnt].T[1:],sens[0]), np.multiply(a[cnt],1-a[cnt])))
		# Calculate weight update gradients for each layer
		grad = []
		for cnt in range(self.L-1):
			grad.append(np.dot(sens[cnt][:,None], np.insert(a[cnt],0,1,axis=0)[:,None].T))
		return grad

	def trainOnData(self, filepath):
		"""Train neural network using data at filepath."""
		x = []
		y_tmp = []
		# Parse data at filepath into training arrays
		if os.path.isfile(filepath):
			with open(filepath, 'r') as f:
				for line in f.readlines():
					tmp = [float(x) for x in line.strip().split()]
					x.append(tmp[1:])
					y_tmp.append(int(tmp[0]))
		y = np.zeros((len(y_tmp), self.dim[-1]))
		y[np.arange(len(y_tmp)), y_tmp] = 1
		y = y.tolist()
		# Shuffle training data
		zipped = np.array([i for i in zip(x,y)])
		np.random.shuffle(zipped)
		x_rand = []
		y_rand = []
		for _x, _y in zipped.tolist():
			x_rand.append(_x)
			y_rand.append(_y)
		# Train using parsed data
		self.train(x_rand, y_rand)

	def train(self, x, y):
		"""Train with input and expected data arrays."""
		grad = [0*t for t in self.theta]
		reg = self.theta
		m = len(y)
		for n in range(20):
			for i in range(m):
				a = self.forwardPropOne(x[i])
				g = self.backwardProp(a,y[i])
				grad = [grad[k] + g[k] for k in range(self.L-1)]
			for i in range(self.L-1):
				reg[i].T[0] = 0
				self.theta[i] = self.theta[i] - self.learning_rate*(grad[i]/m + self.lambda_reg*reg[i])
		if self.filepath != None:
			pickle.dump(self.theta, open(self.filepath, 'wb'))
		return