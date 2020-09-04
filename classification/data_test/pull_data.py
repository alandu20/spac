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
        'https://www.sec.gov/Archives/edgar/data/1723580/000121390020014492/ea122827-8k_opesacquisition.htm',
        'https://www.sec.gov/Archives/edgar/data/1764711/000126493119000199/paac8k123019.htm',
        'https://www.sec.gov/Archives/edgar/data/1805077/000121390020015680/ea123410-8k_brileyprincipal.htm',
        'https://www.sec.gov/Archives/edgar/data/1704760/000121390019013561/f8k072419_pensareacquisition.htm',
        'https://www.sec.gov/Archives/edgar/data/1744494/000114036120011131/form8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1741231/000121390020012045/ea121761-8k_forummergii.htm',
        'https://www.sec.gov/Archives/edgar/data/1741231/000121390020013975/ea122609-8k_forummerger2.htm',
        'https://www.sec.gov/Archives/edgar/data/1725872/000121390020013032/ea122160-8k_megalithfin.htm',
        'https://www.sec.gov/Archives/edgar/data/1754824/000121390020013781/ea122529-8k_schultzespecial.htm',
        'https://www.sec.gov/Archives/edgar/data/1776903/000121390020016050/ea123558-8k_netfinacq.htm',
        'https://www.sec.gov/Archives/edgar/data/1745317/000110465920044768/tm2015448d1_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1697805/000121390020007859/ea120190-8k_xynomic.htm',
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
        'https://www.sec.gov/Archives/edgar/data/1759631/000121390020015311/ea123187-8k_tortoiseacq.htm',
        'https://www.sec.gov/Archives/edgar/data/1725134/000119312519100029/d585731d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1793659/000119312520199210/d14583d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1725134/000119312520186074/d12451d8k.htm', # definitive agreement
        'https://www.sec.gov/Archives/edgar/data/1720353/000121390019026253/f8k121619_nebulaacquisition.htm', # definitive agreement
        'https://www.sec.gov/Archives/edgar/data/1751143/000121390019024210/f8k111819_boxwoodmerger.htm', # definitive agreement
        'https://www.sec.gov/Archives/edgar/data/1720353/000119312520077317/d901525d8k.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1720353/000156459020013631/nebu-8k_20200326.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1720353/000121390020011900/ea121740-8k_nebulaacq.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1725134/000119312520118283/d920540d8ka.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1682325/000114420419000645/tv510381-8k.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1709682/000121390019015150/f8k072919a1_nescoholdings.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1748252/000121390020002578/f8k020320b_dd3acquisition.htm', # bca amendment
        'https://www.sec.gov/Archives/edgar/data/1718405/000110465920067418/tm2021334d1_8k.htm', # bca vote result
        'https://www.sec.gov/Archives/edgar/data/1704760/000110465920026534/tm2011241-1_8k.htm', # bca vote result
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465919053734/a19-19922_18k.htm', # bca vote date
        'https://www.sec.gov/Archives/edgar/data/1702744/000110465919046862/a19-17478_18k.htm', # purchase agreement
        'https://www.sec.gov/Archives/edgar/data/1653558/000161577418006758/s111503_8k.htm', # purchase agreement; vote result
        'https://www.sec.gov/Archives/edgar/data/1720592/000121390019020337/f8k101119_repayholdingscorp.htm', # purchase agreement
        'https://www.sec.gov/Archives/edgar/data/1735041/000121390019020579/f8k101419_greenlandacqu.htm', # share exchange agreement; vote result
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465919067185/tm1923797d2_8k.htm', # securities purchase agreement
        'https://www.sec.gov/Archives/edgar/data/1723648/000119312520177183/d948881d8k.htm', # merger agreement
        'https://www.sec.gov/Archives/edgar/data/1784535/000121390020019487/ea0124674-8k_proptechacq.htm', # merger agreement
        'https://www.sec.gov/Archives/edgar/data/1708341/000121390020018533/ea124537-8k_allied.htm', # share purchase agreement amendment
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
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419000680/s115401_8k.htm', # also trust account
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419006082/s117569_8k.htm', # also trust account
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419006723/s117785_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1704760/000121390019014728/f8k080219_pensareacqui.htm',
        'https://www.sec.gov/Archives/edgar/data/1682325/000114420418057157/tv505881_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1708341/000168316819002144/brac_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1706946/000114420419034352/tv525003_8ka.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390019013680/f8k072519_gordonpointe.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020001787/f8k012420_gordonpointe.htm',
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020007706/ea120114-8k_gordonpointe.htm', # also trust account
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020011681/ea121637-8k_gordonpointe.htm', # also trust account
        'https://www.sec.gov/Archives/edgar/data/1708176/000121390020012870/ea122063-8k_gordonpointe.htm', # also trust account
        'https://www.sec.gov/Archives/edgar/data/1726293/000143774920011336/pacq20200519_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1653247/000114420418031792/tv495432_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1650575/000121390017003677/f8k041317_pacificspecial.htm', # also trust account
        'https://www.sec.gov/Archives/edgar/data/1691936/000149315220014201/form8-k.htm', # also redemptions
        'https://www.sec.gov/Archives/edgar/data/1690080/000121390020021714/ea125287-8k_kbl.htm',
        'https://www.sec.gov/Archives/edgar/data/1750153/000121390020024002/ea126114-8k_hennessycap4.htm',
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
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465920002029/tm201313-1_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1735041/000121390019021522/f8k102419_greenlandtech.htm',
        'https://www.sec.gov/Archives/edgar/data/1753706/000110465920079050/tm2023499d1_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1706946/000119312519276659/d809452d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1755953/000121390020001486/f8k011520_akernacorp.htm', # closing stock purchase agreement
        'https://www.sec.gov/Archives/edgar/data/1738758/000121390020004184/f8k021520_glorystar.htm', # closing share exchange agreement
    ]
    consummation_path = os.path.join(os.path.dirname(__file__), "consummation")
    for i, url in enumerate(consummation_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(consummation_path):
            os.makedirs(consummation_path)
        file_path_document = consummation_path + "/consummation_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)

    ipo_urls = [
        'https://www.sec.gov/Archives/edgar/data/1804176/000114036120012833/nc10012442x1_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1753706/000121390019008433/f8k051319_act2global.htm',
        'https://www.sec.gov/Archives/edgar/data/1800682/000119312520150173/d933468d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1772757/000114420419027336/tv521878_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1721386/000114420418035644/tv497120_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1779474/000095010319010937/dp111340_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1673481/000161577418004954/s110685_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1780312/000121390019018459/f8k091319_newprovidenceacqu.htm',
        'https://www.sec.gov/Archives/edgar/data/1719489/000119312517372046/d490212d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1802749/000119312520145159/d918309d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1772720/000119312519198970/d766703d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1764301/000114036119014592/form8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1790625/000121390019026119/f8k121019_livcapital.htm',
        'https://www.sec.gov/Archives/edgar/data/1776909/000121390020000127/f8k010320_softwareacq.htm',
        'https://www.sec.gov/Archives/edgar/data/1760683/000121390020004733/f8k021920_eaststoneacq.htm',
        'https://www.sec.gov/Archives/edgar/data/1754824/000161577418014657/s114818_8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1811882/000119312520200108/d46115d8k.htm',
        'https://www.sec.gov/Archives/edgar/data/1816176/000121390020021159/ea125237-8k_goacquisition.htm',
        'https://www.sec.gov/Archives/edgar/data/1816090/000121390020024578/ea126160-8k_ftacolympus.htm',
        'https://www.sec.gov/Archives/edgar/data/1816090/000121390020025273/ea126450-8k_ftacolympus.htm',
    ]
    ipo_path = os.path.join(os.path.dirname(__file__), "ipo")
    for i, url in enumerate(ipo_urls):
        txt = get_request(url, timeout=10).text_content()
        if not os.path.exists(ipo_path):
            os.makedirs(ipo_path)
        file_path_document = ipo_path + "/ipo_%s.txt" % str(i)
        with open(file_path_document, "w") as doc:
            doc.write(txt)

    other_urls = [
        'https://www.sec.gov/Archives/edgar/data/1708341/000168316819001386/brac_8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465919050327/a19-17038_38k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1704760/000161577419003365/s116469_8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1731289/000110465920042727/tm2014949-1_8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1731289/000110465920033164/tm2012695-1_8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1716947/000119312520031371/d850379d8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1751143/000121390019018009/f8k091319_boxwoodmerger.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1697805/000121390018012723/f8k091918_bisoncapitalacq.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1712189/000114420418062119/tv508120_8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1719489/000119312519158991/d731495d8k.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1716947/000121390020001823/f8k012720_leisureacquis.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1713539/000161577419002794/s116244_8ka.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1776903/000121390020019408/ea124710-8ka1_netfinacquis.htm', # presentation
        'https://www.sec.gov/Archives/edgar/data/1736874/000121390020010769/ea121312-8k_hlacquisitions.htm', # trust account
        'https://www.sec.gov/Archives/edgar/data/1768012/000114420419029853/tv523109_8k.htm', # units split to stock + warrants
        'https://www.sec.gov/Archives/edgar/data/1759008/000114420419019546/tv518793_8k.htm', # units split to stock + warrants
        'https://www.sec.gov/Archives/edgar/data/1785041/000114036120000582/form8k.htm', # units split to stock + warrants
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465919063421/a19-22526_18k.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1744894/000110465918068931/a18-40185_18k.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1647088/000164708818000032/ngform8-k93018.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1653558/000162828018014392/a8k-earningsreleasex093020.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1713952/000119312520022132/d880962d8k.htm', # financial results
        'https://www.sec.gov/ix?doc=/Archives/edgar/data/1653558/000165355819000015/a8k-earningsreleasex93.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1702744/000170274419000003/a8-k_q1x2019.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1721741/000149315218011228/form8-k.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1698990/000119312518250666/d606200d8k.htm', # financial results
        'https://www.sec.gov/Archives/edgar/data/1721386/000173112219000514/e1477_8k.htm', # item 2.03 note
        'https://www.sec.gov/Archives/edgar/data/1736874/000121390020017382/ea124130-8k_hlacquisitions.htm', # 2.03 note
        'https://www.sec.gov/Archives/edgar/data/1698990/000119312518254084/d609686d8k.htm', # acquisition
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465920065608/tm2020890d1_8k.htm', # acquisition
        'https://www.sec.gov/ix?doc=/Archives/edgar/data/1713952/000171395220000016/ck0001713952-20200609.htm' # other vote
        'https://www.sec.gov/Archives/edgar/data/1682325/000110465920022978/tm209316-1_8k.htm', # law suit
        'https://www.sec.gov/Archives/edgar/data/96223/000119312519036140/d673385d8k.htm', # compensation
        'https://www.sec.gov/Archives/edgar/data/96223/000119312517383636/d488920d8k.htm', # compensation
        'https://www.sec.gov/Archives/edgar/data/96223/000119312518023812/d474723d8k.htm', # compensation
        'https://www.sec.gov/ix?doc=/Archives/edgar/data/1712189/000110465920030223/tm2011830d1_8k.htm', # compensation
        'https://www.sec.gov/Archives/edgar/data/1787791/000119312520082621/d862918d8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1790625/000095010320005029/dp123677_8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1702744/000170274419000006/smpl_8kx2019xannualxmeeting.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1725255/000110465920064941/tm2020402-1_8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1794621/000119312520136322/d925681d8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1653247/000156459019039788/wtrh-8k_20191104.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1682325/000110465920077029/tm2023505d1_8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1653247/000119312519121095/d738628d8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1668428/000119312518353401/d661018d8k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1721741/000149315218008183/form8-k.htm', # director
        'https://www.sec.gov/Archives/edgar/data/1770251/000121390019022065/f8k110419_orisunacquisition.htm', # exchange listing
        'https://www.sec.gov/Archives/edgar/data/1668428/000114420417060024/tv479911_8k.htm', # exchange listing (bca false positive)
        'https://www.sec.gov/Archives/edgar/data/1725134/000119312518296430/d615432d8k.htm', # exchange listing
        'https://www.sec.gov/Archives/edgar/data/1723580/000121390020000122/f8k010220_opesacquisition.htm', # exchange listing
        'https://www.sec.gov/Archives/edgar/data/1771928/000121390019017043/f8k083019_fellazo.htm', # exchange listing
        'https://www.sec.gov/Archives/edgar/data/1653247/000119312518352277/d677933d8k.htm', # exchange listing
        'https://www.sec.gov/Archives/edgar/data/1713539/000121390019009938/f8k053119_kaixinauto.htm', # exchange listing
        'https://www.sec.gov/Archives/edgar/data/1650575/000121390018009604/f8k072518_borqstechnologies.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/1772757/000110465920026239/tm2011171d1_8k.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/96223/000009622315000010/lnc1stqtr2015form8k.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/96223/000119312515072738/d883733d8k.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/1772757/000110465920066102/tm2020970d1_8k.htm' # other press release
        'https://www.sec.gov/ix?doc=/Archives/edgar/data/1668428/000119312520154605/d886481d8k.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/96223/000119312515072738/d883733d8k.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/96223/000009622318000012/luk8-k3312018.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/96223/000009622314000034/lnc3rdqtrform8k.htm', # other press release
        'https://www.sec.gov/Archives/edgar/data/1720592/000121390019001044/f8k012219b_thunderbridge.htm', # conference call
        'https://www.sec.gov/Archives/edgar/data/1744494/000114036119020930/form8k.htm', # investor meeting
        'https://www.sec.gov/Archives/edgar/data/96223/000119312516730524/d187183d8k.htm', # investor meeting
        'https://www.sec.gov/Archives/edgar/data/1720353/000121390020011529/ea121610-8ka_nebulaacquisit.htm', # correction
        'https://www.sec.gov/Archives/edgar/data/1773086/000110465920048708/tm2016303d1_8k.htm', # assignment agreement
        'https://www.sec.gov/Archives/edgar/data/1764046/000110465920027513/tm206490d4_8k.htm', # credit agreement
        'https://www.sec.gov/Archives/edgar/data/1653247/000119312519152361/d720593d8k.htm', # underwriting agreement
        'https://www.sec.gov/Archives/edgar/data/1712189/000110465919019703/a19-6812_48k.htm', # item 4.01
    ]

    gnn_urls = [
        'https://www.globenewswire.com/news-release/2020/08/11/2076409/0/en/Esports-Entertainment-Group-Signs-LOI-to-Acquire-Assets-of-FLIP-Sports.html',
    ]


if __name__ == "__main__":
    main()
