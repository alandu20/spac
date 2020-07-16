import sec_scraper


def main():
    

    c = sec_scraper.Company("Forum Merger II Corp", "1741231")

    filings = c.get_all_filings("8-K")
    for f in filings:
        print(f.accepted_date)
        print(f.documents)


if __name__ == "__main__":
    main()
