from classification import preprocess
from classification import document
import sec_scraper
from lxml import html
import requests
import lxml
import os


def get_request(url: str, timeout: int) -> lxml.html.HtmlElement:
    """Send request to server and output response in HtmlElement."""
    page = requests.get(url, timeout=timeout)
    return html.fromstring(page.content)


def main():
    txt = open("classification/data_test/loi/loi_1.txt", "r").read()

    print(preprocess.preprocess_document(txt))


    # loi_urls = [
    #     'https://www.sec.gov/Archives/edgar/data/1725134/000119312520186074/d12451d8k.htm',
    #     ' https://www.sec.gov/Archives/edgar/data/1723580/000121390020014492/ea122827-8k_opesacquisition.htm',
    # ]
    # loi_path = "classification/data_test/loi"
    # for i, url in enumerate(loi_urls):
    #     txt = get_request(url, timeout=10).text_content()
    #     if not os.path.exists(loi_path):
    #         os.makedirs(loi_path)
    #     file_path_document = loi_path + "/loi_%s.txt" % str(i)
    #     with open(file_path_document, "w") as doc:
    #         doc.write(txt)




    # sec_map = sec_scraper.SEC()
    # company_name = sec_map.get_name_by_ticker("FMCI")
    # cik = sec_map.get_cik_by_ticker("FMCI")
    # co = sec_scraper.Company(company_name, cik)
    # filings = co.get_all_filings("8-K")
    #
    # txt = preprocess.preprocess_document(filings[0].documents[0])
    #
    # print(preprocess.parse_vote_results(txt))



    # subheaders = preprocess.get_item_subheaders(txt)
    # print(subheaders)
    # import pprint
    # pprint.pprint(preprocess.parse_items_mapping(txt))


if __name__ == "__main__":
    main()
