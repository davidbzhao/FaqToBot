
from ANN import BasicNeuralNetwork as BasicNeuralNetwork
from bs4 import BeautifulSoup as bs
from collections import deque
from DataGeneration import DataGenerator
from HtmlFeatureExtractor import HtmlFeatureExtractor
from urllib.error import URLError
import urllib.request as urlre


def urlStandardize(url):
    """Return url string without protocol or trailing slash."""
    try:
        i = url.index('http://')
        url = url[i + len('http://'):]
    except ValueError:
        pass
    try:
        i = url.index('https://')
        url = url[i + len('https://'):]
    except ValueError:
        pass
    if url[-1] == '/':
        url = url[:-1]
    return url


def trainNN(filepath):
    """Return neural network trained on specified training set."""
    nn = BasicNeuralNetwork()
    nn.trainOnData(filepath)
    return nn


def isFaq(url, html, base_url, nn):
    """Determine if page pointed to by url contains an FAQ section.

    The neural network used to guess if there is an FAQ or not has 5 features:
    (1) the number of questions, superficially defined as a text with a question mark and a who, what, where...
    (2) if FAQ or Frequently Asked Questions is in the title
    (3) the number of times FAQ or Frequently Asked Questions in the form of non-anchor tags appears in page
    (4) the number of anchor tags with links with same-page hashes
    (5) if FAQ or Frequently Asked QUestions is in the url
    """
    hfe = HtmlFeatureExtractor(html, base_url)
    input_vec = [
        hfe.getNumberOfQuestions(),
        hfe.getFaqInTitle(),
        hfe.getNumberOfFaqs(),
        hfe.getNumberofHashAnchors(),
        hfe.getFaqInUrl(url)]
    return nn.predict(input_vec)


def crawl(base_url, nn, page_limit=50):
    """Crawl breadth-first through website through anchor links to find FAQ pages.

    base_url -- the base url without the relative url
    nn -- the trained neural network to determine if page is FAQ
    page_limit -- the maximum number of pages to process (default 50)
    """
    faq_urls = []
    visited = []
    url_queue = deque([base_url])

    while url_queue:
        current_url = url_queue.popleft()
        if urlStandardize(current_url) in visited:
            continue
        try:
            # Check if current page is FAQ
            html = bs(urlre.urlopen(current_url), 'html.parser')
            hfe = HtmlFeatureExtractor(html, base_url)
            if isFaq(current_url, html, base_url, nn):
                faq_urls.append(urlStandardize(current_url))
            visited.append(urlStandardize(current_url))

            # Add links from current page
            current_page_links = hfe.getListOfInternalLinks(current_url)
            for link in current_page_links:
                url_queue.append(link)

            # Break if page limit hit
            if len(visited) >= page_limit:
                break
        except URLError:
            pass
    if len(visited) >= page_limit:
        print('Page limit of ' + str(page_limit) + ' was hit.')
    print('Visited ' + str(len(visited)) + ' unique pages.')
    print('About ' + str(len(faq_urls)) +
          ' of those pages are likely FAQ pages.')
    return faq_urls


def potentialFaqsRequest(event, context):
    """Handle events for AWS Lambda."""
    base_url = event['base_url']
    page_limit = int(event['page_limit'])
    nn = trainNN('training.txt')
    faq_urls = crawl(base_url, nn, page_limit)
    return '\n'.join(faq_urls)


if __name__ == '__main__':
    potentialFaqsRequest(
        {'base_url': 'http://ramhacks.vcu.edu/', 'page_limit': '50'}, '')
