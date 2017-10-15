import numpy as np

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
        np.random.shuffle(data)
        partitions = np.linspace(0, len(data), 6).astype(np.int32)
        best_test_error = float('inf')
        best_coefs = []
        for n in range(1, len(partitions)):
            test_data = data[partitions[n-1]:partitions[n]]
            mask = np.ones(len(data))
            mask[np.arange(partitions[n-1], partitions[n])] = 0
            training_data = data[mask == 1]
            coefs = np.linalg.lstsq(training_data[:,1:], training_data[:,0])[0]
            error = self.error(test_data, coefs)
            if error < best_test_error:
                best_test_error = error
                best_coefs = coefs
        self.coefs = coefs
            
    def error(self, test_data, coefs):
        error = 0
        for pt in test_data:
            error = (np.dot(coefs, pt[1:]) - pt[0])**2
        return error / len(test_data)

    def predict(self, input_data):
        prob = np.dot(self.coefs, input_data)
        if abs(prob-0) < abs(prob-1): return 0
        return 1

    def predict_prob(self, input_data):
        return np.dot(self.coefs, input_data)

if __name__ == '__main__':
    FaqChecker('training.txt')