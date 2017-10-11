import datetime
import json
import time

import requests
import xmltodict
from lxml import html


class Analyzer:
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0',
    }

    LCBO_URL = "http://www.lcbo.com"
    LCBO_XML_URLS = ["/product_en.1.xml", "/product_en.2.xml"]

    BEER_STORE_URL = "http://www.thebeerstore.ca"
    BEER_STORE_SEARCH_SUFFIX = "/beers/search/beer_type--"
    BEER_STORE_CATEGORIES = ["Ale", "Lager", "Malt", "Stout"]

    def get_items(self, get_lcbo=True, get_beer_store=True, use_existing_drinks=True):
        try:
            self.items = json.load(open('drinks.json')) if use_existing_drinks else []
            self.items = list(map(lambda x: Drink(**x), self.items))
            self._dump_items(filename='drinks_1.json', dump_errors=False)
        except FileNotFoundError:
            self.items = []
        self.errors = []
        if get_beer_store:
            self.errors += list(self._load_beer_store_items())
        if get_lcbo:
            self.errors += list(self._load_lcbo_items())
        self._dump_items()
        self._dump_html()
        return self.items

    def _dump_items(self, filename='drinks.json', dump_errors=True, error_filename='errors.json'):
        if '_dump_items_counter' not in self.__dict__:
            self.__dump_items_counter = -1
        self.__dump_items_counter += 1
        if self.__dump_items_counter % 20 == 0:
            json.dump([e.to_json() for e in list(self.items)], open(filename, "w+"))
            if dump_errors:
                json.dump(self.errors, open(error_filename, "w+"))

    def _dump_html(self, filename='drinks.html'):
        if '__dump_html_counter' not in self.__dict__:
            self.__dump_html_counter = -1
        self.__dump_html_counter += 1
        if self.__dump_html_counter % 100 == 0:
            open(filename, 'w+').write(analyzer.to_html(self.items))

    def _get_page(self, url):
        try:
            return requests.get(url, headers=self.REQUEST_HEADERS)
        except:
            return None

    def _get_lcbo_urls(self, from_file=False, save_links=True):
        if from_file:
            return json.load(open("lcbo_links.json"))
        else:
            products = []
            for xml_url in self.LCBO_XML_URLS:
                xml = requests.get(self.LCBO_URL + xml_url, headers=self.REQUEST_HEADERS)
                results = xmltodict.parse(xml.text)
                products += list(map(dict, results['urlset']['url']))
            if save_links:
                json.dump(products, open("lcbo_links.json", "w+"))
            return products

    def _load_lcbo_items(self):
        products = self._get_lcbo_urls(from_file=True)
        existing = [e.url for e in list(self.items)]
        i = 0
        for product in products:
            i += 1
            if product['loc'] in existing:
                continue
            print(product['loc'])
            for j in range(5):
                page = self._get_page(product['loc'])
                if page:
                    break
                time.sleep(4)
            else:
                yield [product['loc'], "Connection Error"]
                continue

            try:
                drink = Drink.from_lcbo_page(page.text, product['loc'])
                if drink:
                    self.items.append(drink)
                self._dump_items()
                self._dump_html()
            except Exception as ex:
                print(ex)
                yield [product, ex]

    def _load_beer_store_items(self):
        beers = []
        for beer in self.BEER_STORE_CATEGORIES:
            url = self.BEER_STORE_URL + self.BEER_STORE_SEARCH_SUFFIX + beer
            page = self._get_page(url)
            page = html.fromstring(page.text)
            beers += page.xpath('//a[@class="brand-link teaser"]/@href')
        existing = [e.url for e in list(self.items)]
        i = 0
        for beer in beers:
            i += 1
            url = self.BEER_STORE_URL + beer
            if url in existing:
                continue
            print(url)
            for j in range(5):
                page = self._get_page(url)
                if page:
                    break
                time.sleep(4)
            else:
                yield [url, "Connection Error"]
                continue

            try:
                drink = Drink.from_beer_store_page(page.text, url)
                if drink:
                    self.items += drink
                self._dump_items()
                self._dump_html()
            except Exception as ex:
                print(ex)
                yield [beer, ex]

    @staticmethod
    def to_html(items):
        dump_str = ""
        date = "This list was created created on " + str(datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")) + \
               " and has " + str(len(items)) + " items."
        dump_str += "<html>" \
                    "<head>" \
                    "<script src='http://www.kryogenix.org/code/browser/sorttable/sorttable.js'></script>" \
                    "</head>" \
                    "<body>" \
                    "<b>" + date + "</b><table class='sortable'>"

        dump_str += "<tr style='font-weight:bold'>"
        for header in ["Name", "Category", "Source", "ABV", "Price", "Quantity", "Single mL", "Total mL",
                       "mL/$", "Alc mL", "mL(alc)/$"]:
            dump_str += "<td>" + header + "</td>"
        dump_str += "</tr>"

        for item in items:
            dump_str += "<tr>"
            for elem in [item.name, item.category, item.source, item.abv, item.price, item.quantity, item.single_vol,
                         item.total_vol,
                         item.ml_per_dollar, item.alcohol_vol, item.alc_per_dollar]:
                if isinstance(elem, float):
                    elem = round(elem, 2)
                if elem is item.name:
                    elem = '<a href="' + item.url + '">' + elem + "</a>"
                dump_str += "<td>" + str(elem) + "</td>"
            dump_str += "</tr>"

        dump_str += "</table></body></html>"
        return dump_str


class Drink:
    def __init__(self, name, category, abv, price, source, quantity, single_vol, url):
        self.name = str(name).encode('ascii', 'ignore').decode("utf-8")
        self.category = str(category).encode('ascii', 'ignore').decode("utf-8")
        self.abv = float(abv)
        self.price = float(price)
        self.source = str(source).encode('ascii', 'ignore').decode("utf-8")
        self.quantity = int(quantity)
        self.single_vol = float(single_vol)
        self.url = str(url).encode('ascii', 'ignore').decode("utf-8")
        self._update()

    def _update(self):
        self.total_vol = self.quantity * self.single_vol
        self.ml_per_dollar = self.total_vol / self.price
        self.alcohol_vol = self.total_vol * (self.abv / 100)
        self.alc_per_dollar = self.alcohol_vol / self.price

    def to_json(self):
        return {
            "name":       self.name,
            "category":   self.category,
            "abv":        self.abv,
            "price":      self.price,
            "source":     self.source,
            "quantity":   self.quantity,
            "single_vol": self.single_vol,
            "url":        self.url
        }

    @staticmethod
    def from_lcbo_page(text, url):
        page = html.fromstring(text)
        name = page.xpath('//li[@id="categoryPath"]/text()')[0].strip().encode('ascii', 'ignore')
        container = ''.join(page.xpath('//dt[@class="product-volume"]/text()'))
        details = page.xpath('//div[@class="product-details-list"]/dl/dd/text()')
        price = float(
            page.xpath('//div[@id="prodPrices"]/strong/span/span[@class="price-value"]/text()')[0].strip('$').replace(
                ",", ""))
        category = page.xpath('//div[@class="breadcrumbs"]/nav/ul/li/a/text()')
        category = category[min(2, len(category) - 1)]

        try:
            abv = float(details[["%" in i for i in details].index(True)].split("%")[0])
        except IndexError as ex:
            print("No ABV Value")
            return None

        if " x" in container:
            quantity = int(container.split(" x")[0])
        else:
            quantity = 1
        if " x" in container:
            single_vol = int(container.split("x ")[1].split(" mL")[0])
        else:
            single_vol = int(container.split(" ")[0])

        return Drink(name, category, abv, price, "LCBO", quantity, single_vol, url)

    @staticmethod
    def from_beer_store_page(text, url):
        page = html.fromstring(text)

        name = page.xpath('//div[@class="only-desktop"]/h1[@class="page-title"]/text()')[0]
        abv = float(page.xpath('//div[@class="brand-info-inner"]/dl/dd/text()')[-1].split("%")[0])

        options = page.xpath('//tbody/tr/td/text()')
        sale_prices = page.xpath('//tbody/tr/td/strike/text()')
        cat = page.xpath('//p[@class="introduction"]/span/text()')
        for beer_type in ["Ale", "Lager", "Malt", "Stout"]:
            if any([beer_type in e for e in cat]):
                cat = beer_type
                break
        else:
            cat = cat[0]

        if len(sale_prices) > 0:
            to_insert = []
            for i in range(len(options)):
                if len(options) == 1 or ("ml" in options[i] and (i == len(options) - 1 or "$" not in options[i + 1])):
                    to_insert.append([i + 1, sale_prices.pop(0)])

            i = 0
            for e in to_insert:
                options.insert(e[0] + i, e[1])
                i += 1

        for i in range(0, len(options), 2):
            container_type = options[i]
            price = float(options[i + 1].split("$")[1].replace(",", ""))
            quantity = int(container_type.split("  ")[0])
            single_vol = int(container_type.split(" ")[-1][0:-3])

            # Deposit on keg return
            if single_vol in [30000, 50000, 58600]:
                price -= 50
            if single_vol in [20000, 25000]:
                price -= 20

            yield Drink(name, cat, abv, price, "The Beer Store", quantity, single_vol, url)


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.get_items()
