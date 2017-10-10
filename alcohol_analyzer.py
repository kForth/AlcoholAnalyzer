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
