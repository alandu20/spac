import os
import pandas as pd
import sec_scraper


BASE_PATH = "data/sec_filings"


def get_old_spac_tickers(file_path):
    """Get list of old spac tickers."""
    # Past spac list (completed business combination).
    spac_list_past = pd.read_csv(file_path)
    spac_list_past.fillna('missing', inplace=True)
    spac_list_past['dupe_filter'] = spac_list_past['Old Ticker'] + \
                                    spac_list_past['New Ticker']
    spac_list_past = spac_list_past[
        spac_list_past.dupe_filter.isin(spac_list_past.dupe_filter.unique())]
    spac_list_past.drop(columns=['dupe_filter'], inplace=True)
    return spac_list_past['Old Ticker'].to_list()


def get_current_spac_tickers(file_path):
    """Get list of new spac tickers."""
    # Current spac list.
    spac_list_current = pd.read_csv(file_path)
    spac_list_current = spac_list_current.Ticker.unique()
    spac_list_current = pd.DataFrame(spac_list_current, columns=['Ticker'])
    return spac_list_current['Ticker'].to_list()


def main():
    # Instantiate SEC map.
    sec_map = sec_scraper.SEC()

    # File paths.
    file_path_current = 'data/spac_list_current.csv'
    file_path_past = 'data/spac_list_past.csv'

    for spac in get_old_spac_tickers(file_path_past):
        print(spac)
        try:
            company_name = sec_map.get_name_by_ticker(spac)
            cik = sec_map.get_cik_by_ticker(spac)
        except ValueError:
            continue

        # Track file path for company
        file_path_company = BASE_PATH + "/%s" % spac

        # Get filings.
        c = sec_scraper.Company(company_name, cik)
        filings = c.get_all_filings("8-K")

        # Dump out text data.
        for filing in filings:
            file_path_filing = file_path_company + "/%s" % filing.accepted_date
            if not os.path.exists(file_path_filing):
                os.makedirs(file_path_filing)
            file_path_document = file_path_filing + "/%s" % "8-K.txt"
            with open(file_path_document, "w") as doc:
                doc.write(filing.documents[0])


if __name__ == "__main__":
    main()
