import json

import requests
import xmltodict
from lxml import html


class Drink:
    def __init__(self, name, abv, price, source, quantity, single_vol):
        self.name = name
        self.abv = abv
        self.price = price
        self.source = source
        self.quantity = quantity
        self.single_vol = single_vol
        self._update()

    def _update(self):
        self.total_vol = self.quantity * self.single_vol
        self.price_per_vol = self.price / self.total_vol
        self.alcohol_vol = self.total_vol * (self.abv / 100)
        self.price_per_alc = self.price / self.alcohol_vol

    def to_json(self):
        return {
            "name":          self.name,
            "abv":           self.abv,
            "price":         self.price,
            "source":        self.source,
            "quantity":      self.quantity,
            "single_vol":    self.single_vol,
            "total_vol":     self.total_vol,
            "price_per_vol": self.price_per_vol,
            "alcohol_vol":   self.alcohol_vol,
            "price_per_alc": self.price_per_alc
        }

    @staticmethod
    def from_lcbo_page(text):
        page = html.fromstring(text)
        name = page.xpath('//li[@id="categoryPath"]/text()')[0].strip().encode('ascii', 'ignore')
        container = ''.join(page.xpath('//dt[@class="product-volume"]/text()'))
        details = page.xpath('//div[@class="product-details-list"]/dl/dd/text()')
        abv = float(details[["%" in i for i in details].index(True)].split("%")[0])
        price = float(page.xpath('//div[@id="prodPrices"]/strong/span/span[@class="price-value"]/text()')[0].strip('$'))

        if " x" in container:
            quantity = int(container.split(" x")[0])
        else:
            quantity = 1
        if " x" in container:
            single_vol = int(container.split("x ")[1].split(" mL")[0])
        else:
            single_vol = int(container.split(" ")[0])

        return Drink(name, abv, price, "LCBO", quantity, single_vol)

    @staticmethod
    def from_beer_store_page(text):
        page = html.fromstring(text)

        name = page.xpath('//div[@class="only-desktop"]/h1[@class="page-title"]/text()')[0]
        abv = float(page.xpath('//div[@class="brand-info-inner"]/dl/dd/text()')[-1].split("%")[0])

        options = page.xpath('//tbody/tr/td/text()')
        sale_prices = page.xpath('//tbody/tr/td/strike/text()')

        if len(sale_prices) > 0:
            to_insert = []
            for i in range(len(options)):
                if len(options) == 1 or ("ml" in options[i] and (i == len(options) - 1 or not "$" in options[i + 1])):
                    to_insert.append([i + 1, sale_prices.pop(0)])

            i = 0
            for e in to_insert:
                options.insert(e[0] + i, e[1])
                i += 1

        containers = []
        for i in range(0, len(options), 2):
            container_type = options[i]
            price = float(options[i + 1].split("$")[1])
            quantity = int(container_type.split("  ")[0])
            single_vol = int(container_type.split(" ")[-1][0:-3])

            if single_vol in [50000, 58600]:
                price -= 50
            if single_vol in [30000]:
                price -= 50
            if single_vol in [20000, 25000]:
                price -= 20

            containers.append(Drink(name, abv, price, "The Beer Store", quantity, single_vol))
        return containers


class Analyzer:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0',
    }
    LCBO_URL = "http://www.lcbo.com"
    LCBO_XML_URLS = ["/product_en.1.xml", "/product_en.2.xml"]

    def __init__(self):
        pass

    def get_lcbo_urls(self, from_file=False, save_links=True):
        if from_file:
            return json.load(open("links.json"))
        else:
            products = []
            for xml_url in self.LCBO_XML_URLS:
                xml = requests.get(self.LCBO_URL + xml_url, headers=self.HEADERS)
                results = xmltodict.parse(xml.text)
                products += map(dict, results['urlset']['url'])
            if save_links:
                json.dump(products, open("links.json", "w+"))
            return products

    def get_lcbo_items(self):
        items = []
        products = self.get_lcbo_urls(from_file=True)

        for product in products[:3]:
            page = requests.get(product['loc'], headers=self.HEADERS)
            items.append(Drink.from_lcbo_page(page.text))

        return items


if __name__ == "__main__":
    analyzer = Analyzer()
    json.dump(analyzer.get_lcbo_items(), open('links.json'))
