from bs4 import BeautifulSoup as bs
import urllib.request as urlre
from HtmlFeatureExtractor import HtmlFeatureExtractor
from ANN import BasicNeuralNetwork as BasicNeuralNetwork
from DataGeneration import DataGenerator
from collections import deque

PAGE_LIMIT = 10

def urlStandardize(url):
    try:
        i = url.index('http://')
        url = url[i + len('http://'):]
    except ValueError: pass
    try:
        i = url.index('https://')
        url = url[i + len('https://'):]
    except ValueError: pass
    if url[-1] == '/': url = url[:-1]
    return url

def trainNN():
    nn = BasicNeuralNetwork('weights.pickle')
    x = [[2,0,0,21], [0,0,0,14], [0,0,1,0], [24,0,0,47], [0,0,0,0], [102,0,1,0], [10,0,0,19], [1,0,0,14], [4,0,1,8], [9,0,2,7], [9,0,4,11], [17,0,4,19], [3,1,4,1], [11,1,26,0], [16,0,2,9], [17,1,6,3]]
    y = [[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
    nn.train(x,y)

def isFaq(url, html):
    hfe = HtmlFeatureExtractor(html, baseUrl)
    print(hfe.getListOfInternalLinks(url))
    ## Neural network
    # Features;
    #   (1) number of question marks
    #   (2) if FAQ or Frequently Asked Questions is in the title
    #   (3) how many times FAQ or Frequently Asked Questions is on the page
    #   (4) how many anchor tags with links to hash
    input_vec = [hfe.getNumberOfQuestionMarks(), hfe.getFaqInTitle(), hfe.getNumberOfFaqs(), hfe.getNumberofHashAnchors()]
    nn = BasicNeuralNetwork('weights.pickle')
    return not not (nn.predict(input_vec))

def crawl(baseUrl):
    faq_urls = []
    visited = []
    url_queue = deque()
    url_queue.append(baseUrl)
    while url_queue:
        cur_url = url_queue.popleft()
        if urlStandardize(cur_url) in visited: continue
        html = bs(urlre.urlopen(cur_url), 'html.parser')
        hfe = HtmlFeatureExtractor(html, baseUrl)
        if isFaq(cur_url, html): faq_urls.append(urlStandardize(cur_url))
        visited.append(urlStandardize(cur_url))
        cur_page_links = hfe.getListOfInternalLinks(cur_url)
        for link in cur_page_links:
            url_queue.append(link)
        if len(visited) >= PAGE_LIMIT: break
    print('Visited ' + str(len(visited)) + ' unique pages.')
    print('About ' + str(len(faq_urls)) + ' of those pages are likely FAQ pages.')
    if len(visited) >= PAGE_LIMIT: print('Program hit unique page visits limit of ' + str(PAGE_LIMIT))
    return faq_urls

baseUrl = 'http://ugrad.vcu.edu/'
faq_urls = crawl(baseUrl)