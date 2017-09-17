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
    def getNumberOfQuestions(self):
        count = 0
        for el in self.visible_text_elems:
            try:
                if '?' in el and ('who' in el or 'what' in el or 'when' in el or 'why' in el or 'where' in el or 'how' in el): count += 1
            except UnicodeEncodeError: pass
        return count
        # return (' '.join(self.visible_text_elems)).count('?')

    # feature - is faq in title
    def getFaqInTitle(self):
        title_elem = self.html.find('title')
        if not title_elem: return 0
        title_text = title_elem.text.strip().lower()
        if 'faq' in title_text or ('frequently' in title_text and 'asked' in title_text): return 1
        return 0

    # feature - number of "faq" in page text
    def getNumberOfFaqs(self):
        # text_string =  ' '.join(self.visible_text_elems)
        # return text_string.count('faq') + text_string.count('frequently asked')
        count = 0
        for el in self.html.findAll(text=True):
            try:
                if ('faq' in el.strip().lower() or 'frequently asked' in el.strip().lower()) and \
                    el.name != 'a':
                    count += 1
            except (AttributeError, UnicodeEncodeError) as e: pass
        return count
        # return len([el.text for el in self.html.findAll(text=True) if el.name != 'a' and ('faq' in el.text or 'frequently asked' in el.text)])

    # feature - number of anchor tags linking to hash
    def getNumberofHashAnchors(self):
        count = 0
        for a in self.html.findAll('a', href=True):
            if len(a['href']) > 0 and a['href'][0] == '#':
                for parent in a.parents:
                    if parent is not None and parent.name == 'nav': continue
                count += 1
        return count

    # feature - faq in url
    def getFaqInUrl(self, url):
        if 'faq' in url or ('frequently' in url and 'asked' in url): return 1
        return 0

    def getListOfInternalLinks(self, curUrl):
        links = [a['href'] for a in self.html.findAll('a', href=True) if (len(a['href']) > 0 and a['href'][0] != '#')]
        internal_links = []
        for link in links:
            if link[:4] == 'http' and self.baseUrl in link: internal_links.append(link)
            elif link[:4] == 'http' and self.baseUrl not in link: pass
            elif self.baseUrl not in urljoin(curUrl, link): pass
            elif '.doc' in link or '.pdf' in link or '.xls' in link or '.csv' in link or '.pptx' in link: pass
            else: internal_links.append(urljoin(curUrl, link))
        return internal_links