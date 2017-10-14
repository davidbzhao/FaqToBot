
from FaqChecker import FaqChecker as FaqChecker
from bs4 import BeautifulSoup as bs
from collections import deque
from DataGeneration import DataGenerator
from HtmlFeatureExtractor import HtmlFeatureExtractor
from urllib.error import URLError
import urllib.request as urlre
import sys


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


def isFaq(url, html, base_url, clf):
    """Determine if page pointed to by url contains an FAQ section.

    The neural network used to guess if there is an FAQ or not has 5 features:
    (1) the number of questions, superficially defined as a text with a question mark and a who, what, where...
    (2) the number of times FAQ or Frequently Asked Questions in the form of non-anchor tags appears in page
    (3) if FAQ or Frequently Asked QUestions is in the url
    """
    hfe = HtmlFeatureExtractor(html, base_url)
    input_vec = [
        hfe.getNumberOfQuestions(),
        hfe.getNumberOfFaqs(),
        hfe.getFaqInUrl(url)]
    return clf.predict([input_vec])


def crawl(base_url, clf, page_limit=50):
    """Crawl breadth-first through website through anchor links to find FAQ pages.

    base_url -- the base url without the relative url
    clf -- the trained classifier model to determine if page is FAQ
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
            print(current_url)
            # Check if current page is FAQ
            html = bs(urlre.urlopen(current_url), 'html.parser')
            hfe = HtmlFeatureExtractor(html, base_url)
            if isFaq(current_url, html, base_url, clf):
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
    clf = FaqChecker('training.txt')
    faq_urls = crawl(base_url, clf, page_limit)
    return '\n'.join(faq_urls)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        faq_urls = potentialFaqsRequest({'base_url': sys.argv[1],'page_limit': sys.argv[2]}, '')
        print('FAQ urls')
        print(faq_urls)
    else:
        print('Invalid command line arguments')
