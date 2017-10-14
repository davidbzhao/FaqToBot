from bs4 import BeautifulSoup as bs
from bs4.element import Comment
from urllib.parse import urljoin, urlparse, urlunparse


class HtmlFeatureExtractor:
    def __init__(self, html, base_url):
        """Initialize HFE with details.

        html -- html already parsed by Beautiful Soup
        base_url -- base url without relative url
        """
        self.html = html
        self.filterTextFromHtml()
        self.base_url = self.clean_base_url(base_url)

    def clean_base_url(self, base_url):
        if '.' in base_url and '/' in base_url and base_url[::-1].index('.') < base_url[::-1].index('/'):
            parsed = urlparse(base_url)
            cleaned_path = '/'.join(parsed.path.rsplit('/')[:-1])
            parsed = parsed._replace(path=cleaned_path)
            return urlunparse(parsed)
        return base_url

    def isVisible(self, elem):
        """Return inherent visibility of element."""
        return not (
            elem.parent.name in [
                'style',
                'script',
                'head',
                'meta',
                '[document]'] or isinstance(
                elem,
                Comment))

    def isNotEmpty(self, elem):
        """Return False if element text is only space or empty, otherwise True."""
        return elem.strip() != ''

    def filterTextFromHtml(self):
        """Generate string list of visible text elements."""
        self.visible_text_elems = [
            el.strip().lower() for el in filter(
                self.isNotEmpty, filter(
                    self.isVisible, self.html.findAll(
                        text=True)))]

    def getNumberOfQuestions(self):
        """Return number of questions in page."""
        count = 0
        for el in self.visible_text_elems:
            if '?' in el and (
                    'who' in el or 'what' in el or 'when' in el or 'why' in el or 'where' in el or 'how' in el):
                count += 1
        return count

    # feature - is faq in title
    def getFaqInTitle(self):
        """Return if faq or frequently asked questions is in title."""
        title_elem = self.html.find('title')
        if not title_elem:
            return 0
        title_text = title_elem.text.strip().lower()
        if 'faq' in title_text or (
                'frequently' in title_text and 'asked' in title_text):
            return 1
        return 0

    def getNumberOfFaqs(self):
        """Return number of non-anchor tags containing faq or frequently asked questions."""
        count = 0
        for el in self.html.findAll(text=True):
            if ('faq' in el.strip().lower() or 'frequently asked' in el.strip(
            ).lower()) and el.name != 'a':
                count += 1
        return count

    def getNumberofHashAnchors(self):
        """Return number of anchor tags pointing to a same-page hash link."""
        count = 0
        for a in self.html.findAll('a', href=True):
            if len(a['href']) > 0 and a['href'][0] == '#':
                for parent in a.parents:
                    if parent is not None and parent.name == 'nav':
                        continue
                count += 1
        return count

    def getFaqInUrl(self, url):
        """Return if faq or frequently asked questions is in url."""
        if 'faq' in url or ('frequently' in url and 'asked' in url):
            return 1
        return 0

    def getListOfInternalLinks(self, current_url):
        """Return a list of internal links."""
        links = [a['href'] for a in self.html.findAll('a', href=True) if (
            len(a['href']) > 0 and a['href'][0] != '#')]
        internal_links = []
        for link in links:
            # print(link, end=' -> ')
            # Do not add if external link or non-html document type
            if link[:4] == 'http' and self.base_url in link:
                internal_links.append(link)
                # print('added to internal')
            elif link[:4] == 'http' and self.base_url not in link:
                # print('not http')
                continue
            elif self.base_url not in urljoin(current_url, link):
                # print('%s not in %s' % (self.base_url, urljoin(current_url, link)))
                continue
            elif '.doc' in link or '.pdf' in link or '.xls' in link or '.csv' in link or '.pptx' in link:
                # print('not html')
                continue
            else:
                # print('added to internal')
                internal_links.append(urljoin(current_url, link))
        return internal_links
