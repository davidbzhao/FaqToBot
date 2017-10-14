import numpy as np
from sklearn.linear_model import LinearRegression

class FaqChecker():
    def __init__(self, data_filepath):
        self.train(data_filepath)

    def get_data(self, data_filepath):
        data = []
        with open(data_filepath, 'r') as f:
            data = np.array([[int(x) for x in line.strip().split(' ')] for line in f.readlines()])
        return data

    def train(self, data_filepath):
        data = self.get_data(data_filepath)
        self.model = LinearRegression()
        self.model.fit(data[:,1:], data[:,0])

    def predict(self, input_data):
        prob = self.model.predict(input_data)
        if abs(prob-0) < abs(prob-1): return 0
        return 1

    def predict_prob(self, input_data):
        return self.model.predict(input_data)[0]

if __name__ == '__main__':
    FaqChecker()