from bs4 import BeautifulSoup as bs
from bs4.element import Comment
from urllib.parse import urljoin

class HtmlFeatureExtractor:
    def __init__(self, html, baseUrl):
        # html should be Beautiful Soup parsed already
        self.html = html
        self.filterTextFromHtml()
        self.baseUrl = baseUrl

    def isVisible(self, elem):
        return not (elem.parent.name in ['style', 'script', 'head', 'meta', '[document]'] or \
            isinstance(elem, Comment))

    def isNotEmpty(self, elem):
        return elem.strip() != ''

    def filterTextFromHtml(self):
        self.visible_text_elems = [el.strip().lower() for el in filter(self.isNotEmpty, filter(self.isVisible, self.html.findAll(text=True)))]

    # feature - number of "?" in page text
    def getNumberOfQuestionMarks(self):
        return (' '.join(self.visible_text_elems)).count('?')

    # feature - is faq in title
    def getFaqInTitle(self):
        title_elem = self.html.find('title')
        if not title_elem: return 0
        title_text = title_elem.text.strip().lower()
        if 'faq' in title_text or ('frequently' in title_text and 'asked' in title_text): return 1
        return 0

    # feature - number of "faq" in page text
    def getNumberOfFaqs(self):
        text_string =  ' '.join(self.visible_text_elems)
        return text_string.count('faq') + text_string.count('frequently asked')

    # feature - number of anchor tags linking to hash
    def getNumberofHashAnchors(self):
        return len([a for a in self.html.findAll('a', href=True) if (len(a['href']) > 0 and a['href'][0] == '#')])

    def getListOfInternalLinks(self, curUrl):
        links = [a['href'] for a in self.html.findAll('a', href=True) if (len(a['href']) > 0 and a['href'][0] != '#')]
        internal_links = []
        for link in links:
            try:
                i = link.index('http')
                if link.index(self.baseUrl) == 0: internal_links.append(link)
                else: continue
            except ValueError: pass
            internal_links.append(urljoin(curUrl, link))
        return internal_links