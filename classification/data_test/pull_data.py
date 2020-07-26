from lxml import html
import requests
import lxml
import os


def get_request(url: str, timeout: int) -> lxml.html.HtmlElement:
    """Send request to server and output response in HtmlElement."""
    page = requests.get(url, timeout=timeout)
    return html.fromstring(page.content)


def main():
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
        'https://www.sec.gov/Archives/edgar/data/1776903/000121390020016050/ea123558-8k_netfinacq.htm',
        'https://www.sec.gov/Archives/edgar/data/1745317/000110465920044768/tm2015448d1_8k.htm'
    ]
    loi_path = os.path.join(os.path.dirname(__file__), "loi")
    for i, url in enumerate(loi_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(loi_path):
            os.makedirs(loi_path)
        file_path_document = loi_path + "/loi_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)

    bca_urls = [
        'https://www.sec.gov/Archives/edgar/data/1731289/000110465920028233/tm2011332d1_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1764711/000126493120000025/paac8k031020.htm',
        'https://www.sec.gov/Archives/edgar/data/1764711/000126493120000033/paac8k031620.htm',
        'https://www.sec.gov/Archives/edgar/data/1725134/000119312520115911/d880378d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1759631/000121390020015311/ea123187-8k_tortoiseacq.htm'
    ]
    bca_path = os.path.join(os.path.dirname(__file__), "bca")
    for i, url in enumerate(bca_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(bca_path):
            os.makedirs(bca_path)
        file_path_document = bca_path + "/bca_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)

    extension_urls = [
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419000680/s115401_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419006082/s117569_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419006723/s117785_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1704760/000121390019014728/f8k080219_pensareacqui.htm',
        'https://www.sec.gov/Archives/edgar/data/1682325/000114420418057157/tv505881_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1708341/000168316819002144/brac_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1706946/000114420419034352/tv525003_8ka.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390019013680/f8k072519_gordonpointe.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020001787/f8k012420_gordonpointe.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020007706/ea120114-8k_gordonpointe.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020011681/ea121637-8k_gordonpointe.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020012870/ea122063-8k_gordonpointe.htm'
    ]
    extension_path = os.path.join(os.path.dirname(__file__), "extension")
    for i, url in enumerate(extension_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(extension_path):
            os.makedirs(extension_path)
        file_path_document = extension_path + "/extension_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)

    consummation_urls = [
        'https://www.sec.gov/Archives/edgar/data/1731289/000110465920069434/tm2020911-2_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1731289/000110465920070923/tm2021982d1_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1682325/000114420419014675/tv516340_8k12ba.htm',
        'https://www.sec.gov/Archives/edgar/data/1712189/000110465919016584/a19-6812_18k.htm',
        'https://www.sec.gov/Archives/edgar/data/1709682/000121390019014258/f8k073019_nescoholdings.htm',
        'https://www.sec.gov/Archives/edgar/data/1784797/000114036119020993/nc10006147x2_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465920002029/tm201313-1_8k.htm'
    ]
    consummation_path = os.path.join(os.path.dirname(__file__), "consummation")
    for i, url in enumerate(consummation_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(consummation_path):
            os.makedirs(consummation_path)
        file_path_document = consummation_path + "/consummation_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)


if __name__ == "__main__":
    main()
