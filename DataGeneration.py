from ANN import BasicNeuralNetwork as BasicNeuralNetwork
from bs4 import BeautifulSoup as bs
from HtmlFeatureExtractor import HtmlFeatureExtractor
import urllib.request as urlre
from urllib.error import HTTPError, URLError


class DataGenerator:
    def __init__(self):
        self.fetchPreprocessedData('prepro_training.txt')

    def getBaseUrl(self, url):
        """Get base url from full url."""
        try:
            # A normal url will have two slashes in the protocol and a third after the base url.
            #   http://www.google.com/foobar
            # Remove everything after the third slash.
            #   http://www.google.com/
            third_slash = url.index(
                '/',
                url.index(
                    '/',
                    url.index('/') +
                    1) +
                1)
            return url[:third_slash + 1]
        except ValueError:
            return url

    def fetchPreprocessedData(self, filepath):
        """Fetch preprocessed training urls."""
        print(filepath)
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                y, url = line.strip().split()
                base = self.getBaseUrl(url)
                self.generateTrainingExample(url, base, y)

    def generateTrainingExample(self, url, base, y):
        """Parse page pointed to by url for features."""
        try:
            html = bs(urlre.urlopen(url), 'html.parser')
            hfe = HtmlFeatureExtractor(html, base)
            with open('training.txt', 'a+') as f:
                input_vec = [
                    hfe.getNumberOfQuestions(),
                    hfe.getNumberOfFaqs(),
                    hfe.getFaqInUrl(url)]
                f.write(' '.join([str(y)] + [str(x)
                                             for x in input_vec]) + '\n')
        except (HTTPError, URLError) as e:
            print(url, 'not processed')


if __name__ == '__main__':
    DataGenerator()