import requests
from lxml import html

the_url = "http://www.lcbo.ca/"
page_urls = ["http://www.lcbo.ca/lcbo/catalog/ale/11022",
             "http://www.lcbo.ca/lcbo/catalog/lager/11027",
             "http://www.lcbo.ca/lcbo/catalog/hybrid/11007",
             "http://www.lcbo.ca/lcbo/catalog/specialty/11006",
             "http://www.lcbo.ca/lcbo/catalog/cider/11013",
             "http://www.lcbo.ca/lcbo/catalog/malt-beverages/11501",
             "http://www.lcbo.ca/lcbo/catalog/gift-and-sampler-packs/11002",
             "http://www.lcbo.ca/lcbo/catalog/vodka/11028",
             "http://www.lcbo.ca/lcbo/catalog/whisky-whiskey/11014",
             "http://www.lcbo.ca/lcbo/catalog/rum/11029",
             "http://www.lcbo.ca/lcbo/catalog/gin/11011",
             "http://www.lcbo.ca/lcbo/catalog/brandy/11031",
             "http://www.lcbo.ca/lcbo/catalog/cognac-armagnac/11015",
             "http://www.lcbo.ca/lcbo/catalog/tequila/11020",
             "http://www.lcbo.ca/lcbo/catalog/liqueur-liquor/11019",
             "http://www.lcbo.ca/lcbo/catalog/eau-de-vie/11009",
             "http://www.lcbo.ca/lcbo/catalog/shochu-soju/11023",
             "http://www.lcbo.ca/lcbo/catalog/gift-and-sampler-packs/11024",
             "http://www.lcbo.ca/lcbo/catalog/red-wine/11025",
             "http://www.lcbo.ca/lcbo/catalog/white-wine/11003",
             "http://www.lcbo.ca/lcbo/catalog/rose-wine/11026",
             "http://www.lcbo.ca/lcbo/catalog/champagne/11016",
             "http://www.lcbo.ca/lcbo/catalog/sparkling-wine/11018",
             "http://www.lcbo.ca/lcbo/catalog/dessert-wine/11033",
             "http://www.lcbo.ca/lcbo/catalog/icewine/11032",
             "http://www.lcbo.ca/lcbo/catalog/fortified-wines/11030",
             "http://www.lcbo.ca/lcbo/catalog/specialty-wines/11021",
             "http://www.lcbo.ca/lcbo/catalog/gift-and-sampler-packs/11004",
             "http://www.lcbo.ca/lcbo/catalog/coolers/11012",
             "http://www.lcbo.ca/lcbo/catalog/premixed-cocktails/11001"]

def get_drink_list():
    print "Gathering Drinks."
    drinks = []
    for page_url in page_urls:
        headers = {
            'User-Agent': 'Mozilla/5.0',
        }
        page = requests.get(page_url, headers=headers)
        page = html.fromstring(page.text)

        try:
            num_pages = int(page.xpath('//span[@class="pagination-top"]/span[@class="pages"]/ul/li[@class="hoverover"]/a/text()')[-1])
            urls = []
            for i in range(num_pages+1):
                print page_url + "#contentBeginIndex=0&productBeginIndex=" + str(i*12) + "&beginIndex=" + str(i*12) + "&pageView=&resultType=products&orderByContent=&searchTerm=&facet=&storeId=10151&catalogId=10001&langId=-1&fromPage=&objectId=&requesttype=ajax"
                urls += [page_url + "#contentBeginIndex=0&productBeginIndex=" + str(i*12) + "&beginIndex=" + str(i*12) + "&pageView=&resultType=products&orderByContent=&searchTerm=&facet=&storeId=10151&catalogId=10001&langId=-1&fromPage=&objectId=&requesttype=ajax"]
        except:
            urls = [page_url]

        for url in urls:
            headers = {
                'User-Agent': 'Mozilla/5.0',
            }
            page = requests.get(url, headers=headers)
            page = html.fromstring(page.text)
            l = page.xpath('//div[@class="product-name"]/a/@href')
            drinks += l

    print "\nAnalyzing " + str(len(drinks)) + " Drinks\n"

    drink_list = []
    for drink in drinks:
        print drink.split("/")[-2]
        data = analyze_drink(the_url + drink)
        if data == None:
            continue
        drink_list.append(data)

    return drink_list

def analyze_drink(url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    page = requests.get(url, headers=headers)

    if page.status_code == 403:
        print "."
        return analyze_drink(url)

    if "We're sorry, the page you requested does not exist." in page.text:
        return None

    page = html.fromstring(page.text)

    name = page.xpath('//li[@id="categoryPath"]/text()')[0].strip().encode('ascii', 'ignore')
    container = ''.join(page.xpath('//dt[@class="product-volume"]/text()'))
    details = page.xpath('//div[@class="panel-body"]/dl/dd/text()')
    print details
    abv = details[["%" in i for i in details].index(True)]
    abv_val = float(abv.split("%")[0])

    reg_price = page.xpath('//div[@class="prices col-xs-6"]/small/text()')
    price = -1
    if reg_price == []:
        price = float(page.xpath('//div[@class="prices col-xs-6"]/strong/text()')[0].strip("$"))
    else:
        price = float(reg_price[0].split('$')[-1])

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


    return [name, code, "LCBO", container, round(price,2), quantity, round(single_vol,2), round(total_vol,2), round(price_per_vol,4), round(alcohol_vol,2), round(price_per_alc,4)]


# print get_drink_list()
