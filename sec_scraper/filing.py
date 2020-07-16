from typing import List


class Filing(object):

    def __init__(self, filing_type: str, url: str,
                 filing_date: str, accepted_date: str,
                 period_of_report: str, documents: List[str]):
        """Initialize filing."""
        self.filing_type = filing_type
        self.url = url
        self.filing_date = filing_date
        self.accepted_date = accepted_date
        self.period_of_report = period_of_report,
        self.documents = documents
