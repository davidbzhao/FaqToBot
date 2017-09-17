from bs4 import BeautifulSoup as bs
import urllib.request as urlre
from urllib.error import URLError
from HtmlFeatureExtractor import HtmlFeatureExtractor
from ANN import BasicNeuralNetwork as BasicNeuralNetwork
from DataGeneration import DataGenerator
from collections import deque

PAGE_LIMIT = 50

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
    nn.trainOnData('training.txt')

def isFaq(url, html, baseUrl):
    hfe = HtmlFeatureExtractor(html, baseUrl)
    ## Neural network
    # Features;
    #   (1) number of question marks
    #   (2) if FAQ or Frequently Asked Questions is in the title
    #   (3) how many times non-link FAQ or Frequently Asked Questions is on the page
    #   (4) how many anchor tags with links to hash
    input_vec = [hfe.getNumberOfQuestions(), hfe.getFaqInTitle(), hfe.getNumberOfFaqs(), hfe.getNumberofHashAnchors(), hfe.getFaqInUrl(url)]
    nn = BasicNeuralNetwork('weights.pickle')
    prediction = nn.predict(input_vec)
    # print(nn.forwardPropOne(input_vec)[0])
    # print(prediction)
    return (nn.predict(input_vec))

def crawl(baseUrl):
    faq_urls = []
    visited = []
    url_queue = deque()
    url_queue.append(baseUrl)
    while url_queue:
        cur_url = url_queue.popleft()
        if urlStandardize(cur_url) in visited: continue
        print(cur_url)
        try:
            html = bs(urlre.urlopen(cur_url), 'html.parser')
            hfe = HtmlFeatureExtractor(html, baseUrl)
            if isFaq(cur_url, html, baseUrl): faq_urls.append(urlStandardize(cur_url))
            visited.append(urlStandardize(cur_url))
            cur_page_links = hfe.getListOfInternalLinks(cur_url)
            for link in cur_page_links:
                url_queue.append(link)
            if len(visited) >= PAGE_LIMIT: break
        except URLError: pass
    if len(visited) >= PAGE_LIMIT: print('Page limit of ' + str(PAGE_LIMIT) + ' was hit.')
    print('Visited ' + str(len(visited)) + ' unique pages.')
    print('About ' + str(len(faq_urls)) + ' of those pages are likely FAQ pages.')
    return faq_urls

def potentialFaqsRequest(event, context):
    baseUrl = event['baseUrl']
    trainNN()
    faq_urls = crawl(baseUrl)
    print(faq_urls)
    # print('hello world')
    return '\n'.join(faq_urls)