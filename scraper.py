from bs4 import BeautifulSoup as bs
import urllib.request as urlre
from urllib.error import URLError
from HtmlFeatureExtractor import HtmlFeatureExtractor
from ANN import BasicNeuralNetwork as BasicNeuralNetwork
from DataGeneration import DataGenerator
from collections import deque


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
    nn = BasicNeuralNetwork()
    nn.trainOnData('training.txt')
    return nn

def isFaq(url, html, base_url, nn):
    hfe = HtmlFeatureExtractor(html, base_url)
    ## Neural network
    # Features;
    #   (1) number of questions, superficially defined as a text with a question mark and a who, what, where...
    #   (2) if FAQ or Frequently Asked Questions is in the title
    #   (3) how many times FAQ or Frequently Asked Questions in the form of non-anchor tags appears in page
    #   (4) how many anchor tags with links to hash links
    #   (5) if FAQ or Frequently Asked QUestions is in the url
    input_vec = [hfe.getNumberOfQuestions(), hfe.getFaqInTitle(), hfe.getNumberOfFaqs(), hfe.getNumberofHashAnchors(), hfe.getFaqInUrl(url)]
    # nn = BasicNeuralNetwork()
    prediction = nn.predict(input_vec)
    return (nn.predict(input_vec))

def crawl(base_url, nn, page_limit=50):
    faq_urls = []
    visited = []
    url_queue = deque()
    url_queue.append(base_url)
    while url_queue:
        cur_url = url_queue.popleft()
        if urlStandardize(cur_url) in visited: continue
        print(cur_url)
        try:
            html = bs(urlre.urlopen(cur_url), 'html.parser')
            hfe = HtmlFeatureExtractor(html, base_url)
            if isFaq(cur_url, html, base_url, nn): faq_urls.append(urlStandardize(cur_url))
            visited.append(urlStandardize(cur_url))
            cur_page_links = hfe.getListOfInternalLinks(cur_url)
            for link in cur_page_links:
                url_queue.append(link)
            if len(visited) >= page_limit: break
        except URLError: pass
    if len(visited) >= page_limit: print('Page limit of ' + str(page_limit) + ' was hit.')
    print('Visited ' + str(len(visited)) + ' unique pages.')
    print('About ' + str(len(faq_urls)) + ' of those pages are likely FAQ pages.')
    return faq_urls

def potentialFaqsRequest(event, context):
    base_url = event['base_url']
    page_limit = int(event['page_limit'])
    nn = trainNN()
    faq_urls = crawl(base_url, nn, page_limit)
    print('\n'.join(faq_urls))

if __name__ == '__main__':
    potentialFaqsRequest({'base_url':'http://ramhacks.vcu.edu/', 'page_limit':'50'}, '')