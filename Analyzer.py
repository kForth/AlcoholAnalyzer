from operator import itemgetter
import datetime
import BeerStoreAnalyzer
import LcboAnalyzer

def get_beer_store():
    return BeerStoreAnalyzer.get_beer_list()

def get_lcbo():
    return LcboAnalyzer.get_drink_list()

def print_stats_to_html(data, filename):
    data = sorted(data, key=itemgetter(10))
    with open(filename, "w") as f:
        date = "List created: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write("<head><script src='http://www.kryogenix.org/code/browser/sorttable/sorttable.js'></script></head>\n<body>\n<b>" + date + "</b>\n<table class='sortable'>\n")
        f.write("<tr style='font-weight:bold'><td>Name</td><td>Code</td><td>Source</td><td>Type</td><td>Price</td><td>Quantity</td><td>Single Vol</td><td>Total Vol</td><td>Price Per Vol</td><td>Alc Vol</td><td>Price Per Alc</td></tr>")
        for d in data:
            f.write("<tr>")
            for e in d:
                if e == d[1]:
                    if d[2] == "LCBO":
                        f.write("<td><a href='http://lcbo.ca/lcbo/product/" + d[1] + "'>" + str(e) + "</a></td>")
                    elif d[2] == "The Beer Store":
                        f.write("<td><a href='http://thebeerstore.ca/beers/" + d[1] + "'>" + str(e) + "</a></td>")
                    else:
                        f.write("<td>" + str(e) + "</td>")
                else:
                    f.write("<td>" + str(e) + "</td>")
            f.write("</tr>\n")
        f.write("</table>\n</body></html>")

def get_both_list():
    everything = get_beer_store() + get_lcbo()
    print_stats_to_html(everything, 'all_drinks.html')

def get_beer_list():
    print_stats_to_html(get_beer_store(), 'beer_data.html')

def get_lcbo_list():
    print_stats_to_html(get_lcbo(), 'lcbo_data.html')

get_both_list()
