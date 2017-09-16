from bs4 import BeautifulSoup as bs
import urllib.request as urlre
from HtmlFeatureExtractor import HtmlFeatureExtractor
from ANN import BasicNeuralNetwork as BasicNeuralNetwork

class DataGenerator:
    def __init__(self):
        self.data = [
            ['https://en.wikipedia.org/wiki/Triboelectric_effect', 0],
            ['https://www.cs.virginia.edu/~cr4bd/3330/F2017/', 0],
            ['https://news.ycombinator.com/', 0],
            ['http://onlinelibrary.wiley.com/doi/10.1002/leap.1116/full', 0],
            ['http://users.ece.utexas.edu/~adnan/pike.html', 0],
            ['https://www.economist.com/news/science-and-technology/21728888-better-motors-go-better-batteries-electric-motors-improve-more-things', 0],
            ['http://www.anandtech.com/show/11842/western-digital-ships-12-tb-wd-gold-hdd-8-platters-helium', 0],
            ['https://github.com/marshq/europilot', 0],
            ['https://github.com/eclipse/openj9', 1],
            ['http://ramhacks.vcu.edu/', 1],
            ['http://ugrad.vcu.edu/why/faqs/transportation.html', 1],
            ['http://ugrad.vcu.edu/why/faqs/transfers.html', 1],
            ['https://www.google.com/policies/faq/', 1],
            ['http://www.calbar.ca.gov/FAQ', 1],
            ['http://php.net/manual/en/faq.obtaining.php', 1],
            ['https://gov.georgia.gov/faq', 1],
        ]
        self.generateData()

    def generateData(self):
        for url in self.data:
            html = bs(urlre.urlopen(url[0]), 'html.parser')
            hfe = HtmlFeatureExtractor(html)
            print(url[0])
            with open('training.txt', 'a+') as f:
                input_vec = [hfe.getNumberOfQuestionMarks(), hfe.getFaqInTitle(), hfe.getNumberOfFaqs(), hfe.getNumberofHashAnchors()]
                f.write(' '.join([str(url[1])] + [str(x) for x in input_vec]) + '\n')