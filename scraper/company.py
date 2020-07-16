from lxml import html
from typing import List
from scraper import filing
import requests
import lxml


BASE_URL = "https://www.sec.gov"
FILING_TYPES = ["8-K", "10-K"]


def get_request(url: str, timeout=10) -> lxml.html.HtmlElement:
    """"""
    page = requests.get(url, timeout=timeout)
    return html.fromstring(page.content)


def get_documents(filings_page: lxml.html.HtmlElement, no_of_documents=10,
                  debug=False) -> List[filing.Filing]:
    elems = filings_page.xpath(
        '//*[@id="documentsbutton"]')[:no_of_documents]
    result = []
    for elem in elems:
        url = BASE_URL + elem.attrib["href"]
        content_page = get_request(url)
        if debug:
            print("URL:", url)
            print("FORM:", content_page.find_class("formContent")[
                0].text_content())
        url = BASE_URL + content_page.xpath(
            '//*[@id="formDiv"]/div/table/tr[2]/td[3]/a')[0].attrib[
            "href"]
        filing = get_request(url)
        result.append(filing)
    return result


class Company(object):

    def __init__(self, name, cik, timeout=10):
        """Initialize company object, for pulling documents from SEC."""
        self.name = name
        self.cik = cik
        self.url = ("https://www.sec.gov/cgi-bin/browse-edgar?action="
                    "getcompany&CIK=%s" % cik)
        self.timeout = timeout

    def _get(self, url: str) -> requests.Response:
        """Sends get request to given url for response object.

        Given url, query url server with an HTTP request.
        Args:
            url: String url of given server.
        Returns:
            request.Response object which contains the server's response to an
            HTTP request.
        """
        return requests.get(url, timeout=self.timeout)

    def get_filings_url(self, filing_type: str, prior_to="",
                        ownership="include", no_of_entries=100) -> str:
        """Get url for specific type of SEC filing related to company

        Given parameters construct url associated with the constraints for
        the SEC web page which contains all admissible documents.
        Args:
            filing_type: String value for document filing type.
            prior_to: Date constraint on documents.
            ownership: TODO: figure out what this means.
            no_of_entries: Number of documents to show on the webpage.
        Returns:
            String value for the url.
        """
        if filing_type not in FILING_TYPES:
            raise ValueError("not accepted filing type %s" % filing_type)
        url = (self.url + "&type=" + filing_type + "&dateb=" + prior_to +
               "&owner=" + ownership + "&count=" + str(no_of_entries))
        return url

    def get_filings_page(self, filing_type: str, prior_to="",
                         ownership="include",
                         no_of_entries=100) -> lxml.html.HtmlElement:
        """Get HtmlElement object associated w/ SEC query.

        Given parameters construct url associated with the constraints for
        the SEC web page which contains all admissible documents. Then take
        page content and create an HtmlElement object. Example web page here
        https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=
        0001741231&type=8-K&dateb=&owner=include&count=40&search_text=
        Args:
            filing_type: String value for document filing type.
            prior_to: Date constraint on documents.
            ownership: TODO: figure out what this means.
            no_of_entries: Number of documents to show on the webpage.
        Returns:
            HtmlElement representing SEC documents webpage.
        """
        url = self.get_filings_url(filing_type, prior_to, ownership,
                                   no_of_entries)
        page = self._get(url)
        return html.fromstring(page.content)



# c = Company("Forum Merger II Corp", "1741231")
#
#
# tree = c.get_all_filings(filing_type="8-K")
# print(tree.text_content())
#l = c.get_documents(tree, no_of_documents=100, debug=True)
#print(l[0].text_content())
