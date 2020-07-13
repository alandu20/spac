import pandas as pd


URL_SEC_MAPPING = 'https://www.sec.gov/files/company_tickers.json'


def load_sec_mappings() -> pd.DataFrame:
    """Load SEC mapping information.

    Load in JSON file mapping cik id to ticker to company name. Transforms
    all tickers to upper case, and all data is stored in pandas dataframe.
    """
    # Load in SEC mapping of cik id, ticker, and title.
    sec_mapping = pd.read_json(URL_SEC_MAPPING).transpose()
    sec_mapping.ticker = sec_mapping.ticker.str.upper()
    sec_mapping.cik_str = sec_mapping.cik_str.astype(str)
    return sec_mapping


class SEC(object):

    def __init__(self):
        """Initialize function for SEC data."""
        self.sec_mapping = load_sec_mappings()

    def get_name_by_cik(self, cik: str) -> str:
        """Get company name from cik.

        Given cik use SEC company tickers json file to find the corresponding
        company name.
        Args:
            cik: String value of cik.
        Return:
            String value of company name.
        """
        if cik not in self.sec_mapping.cik_str.to_list():
            raise ValueError("cik %s not found in SEC mapping %s"
                             % (cik, URL_SEC_MAPPING))
        else:
            return (self.sec_mapping[self.sec_mapping.cik_str == cik].
                    title.to_list()[0])

    def get_cik_by_name(self, name: str) -> str:
        """Get cik from company name.

        Given company name use SEC company tickers json file to find the
        corresponding cik.
        Args:
            name: String value of company name.
        Return:
            String value of cik.
        """
        if name not in self.sec_mapping.title.to_list():
            raise ValueError("name %s not found in SEC mapping %s"
                             % (name, URL_SEC_MAPPING))
        else:
            return (self.sec_mapping[self.sec_mapping.title == name].
                    cik_str.to_list()[0])

    def get_ticker_by_cik(self, cik: str) -> str:
        """Get company ticker from cik.

        Given cik use SEC company tickers json file to find the corresponding
        company ticker.
        Args:
            cik: String value of cik.
        Return:
            String value of ticker.
        """
        if cik not in self.sec_mapping.cik_str.to_list():
            raise ValueError("cik %s not found in SEC mapping %s"
                             % (cik, URL_SEC_MAPPING))
        else:
            return (self.sec_mapping[self.sec_mapping.cik_str == cik].
                    ticker.to_list()[0])

    def get_cik_by_ticker(self, ticker: str) -> str:
        """Get cik from ticker.

        Given ticker use SEC company tickers json file to find the
        corresponding cik.
        Args:
            ticker: String value of company name.
        Return:
            String value of cik.
        """
        if ticker not in self.sec_mapping.ticker.to_list():
            raise ValueError("ticker %s not found in SEC mapping %s"
                             % (ticker, URL_SEC_MAPPING))
        else:
            return (self.sec_mapping[self.sec_mapping.ticker == ticker].
                    cik_str.to_list()[0])
