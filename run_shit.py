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
    # txt = open("classification/data_test/loi/loi_1.txt", "r").read()
    #
    # print(preprocess.preprocess_document(txt))
    loi_urls = [
        'https://www.sec.gov/Archives/edgar/data/1725134/000119312520186074/d12451d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1723580/000121390020014492/ea122827-8k_opesacquisition.htm',
        'https://www.sec.gov/Archives/edgar/data/1720353/000121390019026253/f8k121619_nebulaacquisition.htm',
        'https://www.sec.gov/Archives/edgar/data/1764711/000126493119000199/paac8k123019.htm',
        'https://www.sec.gov/Archives/edgar/data/1751143/000121390019024210/f8k111819_boxwoodmerger.htm',
        'https://www.sec.gov/Archives/edgar/data/1805077/000121390020015680/ea123410-8k_brileyprincipal.htm',
        'https://www.sec.gov/Archives/edgar/data/1704760/000121390019013561/f8k072419_pensareacquisition.htm',
        'https://www.sec.gov/Archives/edgar/data/1744494/000114036120011131/form8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1741231/000121390020012045/ea121761-8k_forummergii.htm',
        'https://www.sec.gov/Archives/edgar/data/1741231/000121390020013975/ea122609-8k_forummerger2.htm',
        'https://www.sec.gov/Archives/edgar/data/1725872/000121390020013032/ea122160-8k_megalithfin.htm',
        'https://www.sec.gov/Archives/edgar/data/1754824/000121390020013781/ea122529-8k_schultzespecial.htm',
        'https://www.sec.gov/Archives/edgar/data/1776903/000121390020016050/ea123558-8k_netfinacq.htm'
    ]
    loi_path = "classification/data_test/loi"
    for i, url in enumerate(loi_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(loi_path):
            os.makedirs(loi_path)
        file_path_document = loi_path + "/loi_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)




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
