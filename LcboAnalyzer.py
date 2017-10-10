import requests
import json
from lxml import html

the_url = "http://www.lcbo.com"
page_urls = [["http://www.lcbo.com/lcbo/catalog/ale/11022", "beer%2Fcider"],
             ["http://www.lcbo.com/lcbo/catalog/lager/11027", "beer%2Fcider"],
             ["http://www.lcbo.com/lcbo/catalog/hybrid/11007", "beer%2Fcider"],
             ["http://www.lcbo.com/lcbo/catalog/specialty/11006", "beer%2Fcider"],
             ["http://www.lcbo.com/lcbo/catalog/cider/11013", "beer%2Flager"],
             ["http://www.lcbo.com/lcbo/catalog/malt-beverages/62001", "beer%2Fcider"],
             ["http://www.lcbo.com/lcbo/catalog/gift-and-sampler-packs/52501", "beer%2Fcider"],
             ["http://www.lcbo.com/lcbo/catalog/vodka/11028", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/whisky-whiskey/11014", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/rum/11029", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/gin/11011", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/brandy/11031", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/cognac-armagnac/11015", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/tequila/11020", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/liqueur-liquor/11019", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/eau-de-vie/11009", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/shochu-soju/11023", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/gift-and-sampler-packs/11024", "spirits"],
             ["http://www.lcbo.com/lcbo/catalog/red-wine/11025", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/white-wine/11003", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/rose-wine/11026", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/champagne/11016", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/sparkling-wine/11018", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/dessert-wine/11033", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/icewine/11032", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/fortified-wines/11030", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/specialty-wines/11021", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/gift-and-sampler-packs/11004", "wine"],
             ["http://www.lcbo.com/lcbo/catalog/coolers/11012", "coolers"],
             ["http://www.lcbo.com/lcbo/catalog/premixed-cocktails/11001", "coolers"]]


def get_drink_list():
    print("Gathering Drinks.")
    drink_list = []
    for page_info in page_urls:
        page_url = page_info[0]
        cat = page_info[1]
        print(page_url)

        headers = {
            'User-Agent': 'Mozilla/5.0',
        }
        try:
            page = requests.get(page_url, headers=headers)
            page = html.fromstring(page.text)
        except:
            print("Cannot get {}".format(page_url))
            continue

        try:
            num_pages = int(page.xpath(
                '//span[@class="pagination-top"]/span[@class="pages"]/ul/li[@class="hoverover"]/a/text()')[-1])
            print("\t Found {} pages.".format(num_pages))
            urls = []
            sub_cat = page_url.split("/")[5]
            for i in range(num_pages + 1):
                index = str(i * 12)
                urls += [page_url + "#contentBeginIndex=0&productBeginIndex=" + index + "&beginIndex=" + index + "&orderBy=&categoryPath=" + cat + "%2F" + sub_cat +"&pageView=&resultType=products&orderByContent=&searchTerm=&facet=&storeId=10151&catalogId=10001&langId=-1&fromPage=&loginError=&userId=-1002&objectId=&requesttype=ajax"]
        except:
            urls = [page_url]

        print("\nAnalyzing " + str(len(drink_list)) + " Drinks\n")

        for url in urls:
            headers = {
                'User-Agent': 'Mozilla/5.0',
            }
            page = requests.get(url, headers=headers)
            page = html.fromstring(page.text)
            l = page.xpath('//div[@class="product-name"]/a/@href')

            print(l.split("/")[-2])
            data = analyze_drink(the_url + l)
            if data is None:
                continue
            drink_list.append(data)


    return drink_list


    # item_urls = []
    #
    # page = requests.get(self.LCBO_URL, headers=self.HEADERS)
    # page = html.fromstring(page.text)
    #
    # cat_names = page.xpath('//div[@class="main-nav-wide navbar-collapse collapse"]/ul/li/ul/li[@class="dropdown-submenu"]/a/text()')
    # cat_urls = page.xpath('//div[@class="main-nav-wide navbar-collapse collapse"]/ul/li/ul/li[@class="dropdown-submenu"]/a/@href')
    # categories = dict(zip(cat_names, cat_urls))
    #
    # for category, url in list(categories.items())[:29]:
    #     print("Processing {}".format(category))
    #     sub_cat = url.split("/")[2]
    #     main_page = requests.get(self.LCBO_URL + url[:-7], headers=self.HEADERS)
    #     main_page = html.fromstring(main_page.text)
    #     num_pages = main_page.xpath('//span[@class="pagination-top"]/span[@class="pages"]/ul/li[@class="hoverover"]/a/text()')
    #     if num_pages:
    #         num_pages = int(num_pages[-1])
    #     else:
    #         num_pages = 1
    #
    #     page_urls = []
    #     for i in range(num_pages):
    #         index = str(i * 12)
    #         page_urls += [self.LCBO_URL + url[:-7] + "#contentBeginIndex=0&productBeginIndex=" + index + "&beginIndex=" + index + "&orderBy=&categoryPath=wine%2F" + sub_cat + "&pageView=&resultType=products&orderByContent=&searchTerm=&facet=&catalogId=10001&langId=-1&fromPage=&loginError=&objectId=&requesttype=ajax"]
    #
    #     for page_url in page_urls:
    #         print(page_url)
    #         page = requests.get(page_url)
    #         print(page.text)
    #         page = html.fromstring(page.text)
    #
    #         products = page.xpath('//div[@class="row products list-view"]/div[@class="product"]/div[@class="product-wrapper"]/div[@class="product-name"]/a/text()')
    #         print(products)


def analyze_drink(url):
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    page = requests.get(url, headers=headers)

    if page.status_code == 403:
        print(".")
        return analyze_drink(url)

    if "We're sorry, the page you requested does not exist." in page.text:
        return None

    page = html.fromstring(page.text)

    name = page.xpath('//li[@id="categoryPath"]/text()')[0].strip().encode('ascii', 'ignore')
    container = ''.join(page.xpath('//dt[@class="product-volume"]/text()'))
    details = page.xpath('//div[@class="product-details-list"]/dl/dd/text()')
    abv = details[["%" in i for i in details].index(True)]
    abv_val = float(abv.split("%")[0])

    price = page.xpath('//div[@id="prodPrices"]/strong/span[@class="current-price"]/span[@class="price-value"]/text()')[0]
    price = float(price.strip('$'))

    code = '/'.join(url.split("/")[-2:])
    if " x" in container:
        quantity = int(container.split(" x")[0])
    else:
        quantity = 1
    if " x" in container:
        single_vol = int(container.split("x ")[1].split(" mL")[0])
    else:
        single_vol = int(container.split(" ")[0])
    total_vol = quantity * single_vol
    price_per_vol = price / total_vol
    alcohol_vol = total_vol * (abv_val / 100)
    price_per_alc = price / alcohol_vol

    return [name, code, "LCBO", container, round(price, 2), quantity, round(single_vol, 2), round(total_vol, 2),
            round(price_per_vol, 4), round(alcohol_vol, 2), round(price_per_alc, 4)]

# print(get_drink_list())
