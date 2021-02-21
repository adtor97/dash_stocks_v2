# importing the module
from googlesearch import search
import requests
from lxml.html import fromstring
import pandas as pd
# stored queries in a list
query_list = ["Share price forecast","Technical Analysis"]
# save the company name in a variable
#company_name = input("Please provide the stock name:")
# iterate through different keywords, search and print

# Link URL Title retriever usin request and formstring
def Link_title(URL):
  x = requests.get(URL)
  tree = fromstring(x.content)
  #print(tree.findtext('.//title'))
  return tree.findtext('.//title')

def news_dataframe(company_name, query_list=["Share price forecast","Technical Analysis"]):
    url_title = []
    exception_URLS = ["nasdaq"]
    for i in search(company_name,  tld='com', lang='en', num=1,
                    start=0, stop=4, pause=2.0, country='USA', extra_params={"tbm":'nws'}):
        print(i)

        try:
            print(Link_title(i))
            url_title.append([i, Link_title(i)])

        except:
            url_title.append([i, None])


    for j in query_list:
        for i in search(company_name+j,  tld='com', lang='en', num=1,
                        start=0, stop=3, pause=2.0, country='USA'):
            print(i)
            try:
                url_title.append([i, Link_title(i)])

            except:
                url_title.append([i, "no title"])

    df_url_title = pd.DataFrame(url_title, columns = ["link", "google_title"])

    return df_url_title

#print(news_dataframe(company_name))
