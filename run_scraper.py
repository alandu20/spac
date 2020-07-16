import scraper


def main():
    c = scraper.Company("Forum Merger II Corp", "1741231")


    tree = c.get_filings_page(filing_type="8-K")
    print(tree)


if __name__ == "__main__":
    main()
