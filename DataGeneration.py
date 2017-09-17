from bs4 import BeautifulSoup as bs
import urllib.request as urlre
from urllib.error import HTTPError, URLError
from HtmlFeatureExtractor import HtmlFeatureExtractor
from ANN import BasicNeuralNetwork as BasicNeuralNetwork

class DataGenerator:
    def __init__(self):
        self.processData('prepro_training.txt')
        # self.generateData('training.txt')

    def getBaseUrl(self, url):
        try:
            third_slash = url.index('/', url.index('/', url.index('/')+1)+1)
            return url[:third_slash+1]
        except ValueError: return url

    def processData(self, filepath):
        print(filepath)
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                y, url = line.strip().split()
                base = self.getBaseUrl(url)
                self.generateData(url, base, y)

    def generateData(self, url, base, y):
        try:
            html = bs(urlre.urlopen(url), 'html.parser')
            hfe = HtmlFeatureExtractor(html, base)
            with open('training.txt', 'a+') as f:
                input_vec = [hfe.getNumberOfQuestions(), hfe.getFaqInTitle(), hfe.getNumberOfFaqs(), hfe.getNumberofHashAnchors(), hfe.getFaqInUrl(url)]
                f.write(' '.join([str(y)] + [str(x) for x in input_vec]) + '\n')
        except (HTTPError, URLError) as e: print(url, 'not processed')

if __name__ == '__main__':
    DataGenerator()