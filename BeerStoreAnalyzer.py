import requests
from lxml import html
from operator import itemgetter

url = "http://www.thebeerstore.ca"
search_url = "/beers/search/beer_type--"
beer_types = ["Ale", "Lager", "Malt", "Stout"]

def get_beer_list():
    beers = []
    for beer in beer_types:
        print "Gathering all " + beer + "s"
        page = requests.get(url + search_url + beer)
        page = html.fromstring(page.text)

        l = page.xpath('//a[@class="brand-link teaser"]/@href')
        beers += l

    print "\nAnalyzing " + str(len(beers)) + " Beers\n"

    beer_list = []
    for beer in beers:
        print beer.split("/")[-1]
        data = analyze_beer(url + beer)
        beer_list += data

    print_stats_to_html(beer_list)

    # print beer_list.sort()

def print_stats_to_html(data):
    data = sorted(data, key=itemgetter(9))
    with open('data.html', "w") as f:
        f.write("<body>\n<table>\n")
        f.write("<tr style='font-weight:bold'><td>Name</td><td>Code</td><td>Type</td><td>Price</td><td>Quantity</td><td>Single Vol</td><td>Total Vol</td><td>Price Per Vol</td><td>Alc Vol</td><td>Price Per Alc</td></tr>")
        for d in data:
            f.write("<tr>")
            for e in d:
                if e == d[1]:
                    f.write("<td><a href='" + url + "/beers/" + d[1] + "'>" + str(e) + "</a></td>")
                else:
                    f.write("<td>" + str(e) + "</td>")
            f.write("</tr>\n")
        f.write("</table>\n</body>")

def analyze_beer(url):
    page = requests.get(url)
    page = html.fromstring(page.text)

    name = page.xpath('//div[@class="only-desktop"]/h1[@class="page-title"]/text()')[0]
    abv = page.xpath('//div[@class="brand-info-inner"]/dl/dd/text()')[-1]
    abv_val = float(abv.split("%")[0])

    options = page.xpath('//tbody/tr/td/text()')
    sale_prices = page.xpath('//tbody/tr/td/strike/text()')

    if len(sale_prices) > 0:
        to_insert = []
        for i in range(len(options)):
            if len(options) == 1 or ("ml" in options[i] and (i == len(options)-1 or not "$" in options[i+1])):
                to_insert.append([i+1, sale_prices.pop(0)])

        i = 0
        for e in to_insert:
            options.insert(e[0] + i, e[1])
            i += 1

    containers = []
    for i in range(0, len(options), 2):
        container_type = options[i]
        code = url.split("/")[-1]
        price = float(options[i+1].split("$")[1])
        quantity = int(container_type.split("  ")[0])
        single_vol = int(container_type.split(" ")[-1][0:-3])
        total_vol = quantity * single_vol
        price_per_vol = price / total_vol
        alcohol_vol = total_vol * (abv_val / 100)
        price_per_alc = price / alcohol_vol

        if single_vol == 50000 or single_vol == 58600:
            price -= 50
        if single_vol == 30000:
            price -= 50
        if single_vol == 20000 or single_vol == 25000:
            price -= 20

        container_type = str(quantity) + " x " + str(single_vol) + " ml"

        containers.append([name, code, container_type, price, quantity, single_vol, total_vol, price_per_vol, alcohol_vol, price_per_alc])

    return containers


get_beer_list()
# print analyze_beer("http://www.thebeerstore.ca/beers/alpine-lager")
