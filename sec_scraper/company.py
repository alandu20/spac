from datetime import datetime
from lxml import html
from typing import List
from sec_scraper.filing import Filing
import re
import requests
import lxml


BASE_URL = "https://www.sec.gov"
FILING_TYPES = ["8-K", "10-K"]


def get_request(url: str, timeout: int) -> lxml.html.HtmlElement:
    """Send request to server and output response in HtmlElement."""
    page = requests.get(url, timeout=timeout)
    return html.fromstring(page.content)


def extract_date(text: str) -> str:
    """Extract date from text."""
    match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    return match.group()


def extract_date_time(text: str) -> str:
    """Extract date time from text."""
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', text)
    return match.group()


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

        Take page content and create an HtmlElement object. Example web page
        here https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=
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

    def get_all_filings(self, filing_type: str, prior_to="",
                        ownership="include",
                        no_of_documents=10) -> List[Filing]:
        """Get all filings of certain type.

        Using the url, aggregate the documents for each filing, and all other
        relevant data.
        Args:
            filing_type: String value for document filing type.
            prior_to: Date constraint on documents.
            ownership: TODO: figure out what this means.
            no_of_documents: Number of documents to show on the webpage.
        Returns:
            List of filing objects, each of which contains text of relevant
            documents. TODO: add all the documents, currently only uses 8-K
        """
        filings_page = self.get_filings_page(
            filing_type=filing_type,
            prior_to=prior_to,
            ownership=ownership,
            no_of_entries=no_of_documents
        )
        elems = filings_page.xpath(
            '//*[@id="documentsbutton"]')[:no_of_documents]
        all_filings = []
        for elem in elems:
            filing_url = BASE_URL + elem.attrib["href"]
            filing_page = get_request(filing_url, self.timeout)
            filing_page_content = filing_page.find_class("formContent")[
                    0].text_content()

            # Get the relevant dates.
            filing_date = extract_date(
                re.search("Filing Date\n(.*)\n",
                          filing_page_content).group(1))
            filing_date = datetime.strptime(
                filing_date, '%Y-%m-%d')

            accepted_date = extract_date_time(
                re.search("Accepted\n(.*)\n",
                          filing_page_content).group(1))
            accepted_date = datetime.strptime(
                accepted_date, '%Y-%m-%d %H:%M:%S')

            period_of_report = extract_date(
                re.search("Period of Report\n(.*)\n",
                          filing_page_content).group(1))

            # Extract text from documents in filing.
            document_url = (BASE_URL + filing_page.xpath(
                '//*[@id="formDiv"]/div/table/tr[2]/td[3]/a')[0].attrib[
                "href"]).replace('/ix?doc=', '')
            document = get_request(document_url, self.timeout)

            # Construct filing object.
            filing = Filing(
                filing_type=filing_type,
                url=filing_url,
                filing_date=filing_date,
                accepted_date=accepted_date,
                period_of_report=period_of_report,
                documents=[document.text_content()]
            )
            all_filings.append(filing)
        return all_filings
