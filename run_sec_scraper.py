import pandas as pd
import sec_scraper


def main():
    # Instantiate SEC map.
    sec_map = sec_scraper.SEC()

    cik = sec_map.get_cik_by_ticker('KLR')
    company_name = sec_map.get_name_by_ticker('KLR')
    print(cik, company_name)

    c = sec_scraper.Company(company_name, cik)
    filings = c.get_all_filings('8-K', no_of_documents=3)
    for f in filings:
        print(f.accepted_date, f.documents[0])
        break

    # # File paths.
    # file_path_current = 'data/spac_list_current.csv'
    # file_path_past = 'data/spac_list_past.csv'
    #
    # # current spac list
    # spac_list_current = pd.read_csv(file_path_current)
    # spac_list_current = spac_list_current.Ticker.unique()
    # spac_list_current = pd.DataFrame(spac_list_current, columns=['Ticker'])
    #
    # for spac in spac_list_current["Ticker"].to_list():
    #     try:
    #         company_name = sec_map.get_name_by_ticker(spac)
    #         cik = sec_map.get_cik_by_ticker(spac)
    #     except ValueError:
    #         continue
    #     c = sec_scraper.Company(company_name, cik)
    #     filings = c.get_all_filings("8-K")
    #     dates = [f.accepted_date for f in filings]
    #     print(company_name, cik)
    #     print(dates)
    #
    # # past spac list (completed business combination)
    # spac_list_past = pd.read_csv(file_path_past)
    # spac_list_past.fillna('missing', inplace=True)
    # spac_list_past['dupe_filter'] = spac_list_past['Old Ticker'] + \
    #                                 spac_list_past['New Ticker']
    # spac_list_past = spac_list_past[
    #     spac_list_past.dupe_filter.isin(spac_list_past.dupe_filter.unique())]
    # spac_list_past.drop(columns=['dupe_filter'], inplace=True)
    #
    # for spac in spac_list_past['Old Ticker'].to_list():
    #     try:
    #         company_name = sec_map.get_name_by_ticker(spac)
    #         cik = sec_map.get_cik_by_ticker(spac)
    #     except ValueError:
    #         continue
    #     c = sec_scraper.Company(company_name, cik)
    #     filings = c.get_all_filings("8-K")
    #     dates = [f.accepted_date for f in filings]
    #     print(company_name, cik)
    #     print(dates)


if __name__ == "__main__":
    main()
