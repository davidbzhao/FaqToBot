import numpy as np
import os
import pickle

class BasicNeuralNetwork():
	def __init__(self, filepath=None):
		self.dim = [5, 3, 2]
		self.L = len(self.dim)
		self.theta = []
		self.lam = 0.05
		self.learning_rate = 0.003
		self.filepath = filepath
		self.initWeights()
		self.sigmoid = np.vectorize(self.sigmoid)

	# Initialize random weights for each layer
	# An additional bias node is prepended to the first layer in each pair of layers
	# 	If you had layers of dimensions 4, 2, and 1, the weights would be initialized
	#	as arrays of dimensions as such, [[2x5],[1x3]].
	def initWeights(self):
		# if self.filepath == None or not os.path.isfile(self.filepath):
		for cnt in range(self.L-1):
			self.theta.append((np.random.rand(self.dim[cnt+1], self.dim[cnt]+1)-0.5)*5)
		# else:
			# self.theta = pickle.load(open(self.filepath, 'rb'))

	# Apply a sigmoid function to an input z,
	# vectorized to work on numpy structures
	def sigmoid(self, z):
		return 1/(1+np.exp(-z))

	# Forward propagate with x, an input point
	def forwardPropOne(self, x):
		x = np.array(x)
		a = [x]
		for cnt in range(self.L-1):
			x = self.sigmoid(np.dot(self.theta[cnt],np.insert(x,0,1,axis=0)))
			a.append(x)
		return a

	def predict(self, x):
		x = np.array(x)
		for cnt in range(self.L - 1):
			x = self.sigmoid(np.dot(self.theta[cnt], np.insert(x, 0, 1, axis=0)))
		return np.argmax(x)

	# Backward propagate to update weights given
	# the forward propagation activation values, a,
	# and the expected result, y
	def backwardProp(self, a, y):
		y = np.array(y)
		sens = [a[-1]-y] # sensitivities of the cost function to each pre-activation value
						# initialized with the last layer sensitivity of output - expected
		for cnt in range(self.L-2, 0, -1):
			sens.insert(0, np.multiply(np.dot(self.theta[cnt].T[1:],sens[0]), np.multiply(a[cnt],1-a[cnt])))
		grad = []
		for cnt in range(self.L-1):
			grad.append(np.dot(sens[cnt][:,None], np.insert(a[cnt],0,1,axis=0)[:,None].T))
		return grad

	def trainOnData(self, filepath):
		print('Training on data')
		x = []
		y_tmp = []
		if os.path.isfile(filepath):
			with open(filepath, 'r') as f:
				for line in f.readlines():
					tmp = [float(x) for x in line.strip().split()]
					x.append(tmp[1:])
					y_tmp.append(int(tmp[0]))
		y = np.zeros((len(y_tmp), self.dim[-1]))
		y[np.arange(len(y_tmp)), y_tmp] = 1
		y = y.tolist()
		zipped = np.array([i for i in zip(x,y)])
		# print(zipped.tolist())
		np.random.shuffle(zipped)
		# print(zipped.tolist())
		x_rand = []
		y_rand = []
		for _x, _y in zipped.tolist():
			x_rand.append(_x)
			y_rand.append(_y)
		print(len(x_rand), len(y_rand))
		print([len(i) for i in x_rand])
		print([len(i) for i in y_rand])
		self.train(x_rand, y_rand)

	def train(self, x, y):
		print('Train')
		grad = [0*t for t in self.theta]
		reg = self.theta
		m = len(y)
		for n in range(50):
			print('Epoch',n)
			for i in range(m):
				# a = forwardPropOne([[x[0][i]], [x[1][i]]])
				a = self.forwardPropOne(x[i])
				# print('a', a)
				g = self.backwardProp(a,y[i])
				grad = [grad[k] + g[k] for k in range(self.L-1)]
			for i in range(self.L-1):
				reg[i].T[0] = 0
				self.theta[i] = self.theta[i] - self.learning_rate*(grad[i]/m + self.lam*reg[i])
				# print(forwardPropOne(x))
		if self.filepath != None:
			pickle.dump(self.theta, open(self.filepath, 'wb'))
		return