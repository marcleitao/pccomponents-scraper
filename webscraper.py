from bs4 import BeautifulSoup
import slack
import requests

def get_base_url():
    return 'https://www.pccomponentes.pt'

def get_article_url_ref():
    return '/televisoes/lg/oled'

def get_url(article_url_ref):
    return get_base_url() + article_url_ref

def bs_object(data):
    return BeautifulSoup(data, "html.parser")

def get_content(url):
    response = requests.get(url, timeout=10)
    return bs_object(response.content)

def data_file(filename, contentArray):
    with open(filename, 'w+') as outfile:
        json.dump(contentArray, outfile)
    filename.close()

def get_prices_data(articleData):
    data = articleData.find('div', attrs={"id": "priceBlock"})
    price = data.find('div', attrs={"id": "precio-main"})['data-price']
    baseprice = data.find('div', attrs={"id": "precio-main"})['data-baseprice']
    notaxprice = data.find('b', attrs={"class": "no-iva-base"}).text
    return {
        "price": float(price),
        "baseprice": float(baseprice),
        "notaxprice": float(notaxprice.replace(',', '.'))
    }

def approved_model(name):
    for model in ['55C9', '55B9', '55E9', '65C9', '65B9', '65E9']:
        if model in name:
            return True
    return False

def get_articles_data(content):
    dataArr = []
    articleListContent = content.find('div', attrs={"id": "articleListContent"})
    for data in articleListContent.findAll('article'):
        link = data.find('a', attrs={"class", "GTM-productClick"})
        if approved_model(link['data-name']):
            href = link['href']
            articleData = get_content(get_url(href))
            scrapedObject = {
                "name": link.text,
                "url": get_url(href),
                "prices": get_prices_data(articleData)
            }
            inserted = False
            for i in range(len(dataArr)):
                if scrapedObject["prices"]["notaxprice"] < dataArr[i]["prices"]["notaxprice"]:
                    dataArr.insert(i, scrapedObject)
                    inserted = True
                    break
            if not inserted:
                dataArr.append(scrapedObject)
    return dataArr

def handle_message(data):
    dataArr = ''
    for dic in data:
        message = "Article: " + dic["name"] + "\n price: " + str(dic["prices"]["notaxprice"]) + "\n url: " + dic["url"] + "\n--------------------"
        dataArr = dataArr + "\n" + message
    return dataArr

def slack_notify(message):
    client = slack.WebClient(token='<TOKEN>')
    client.chat_postMessage(channel='@<USER>', text=message, username='<USERNAME>', icon_emoji=':robot_face:', as_user='true')

def main():
    content = get_content(get_url(get_article_url_ref()))
    contentArray = get_articles_data(content)
    message = handle_message(contentArray)
    slack_notify(message)

if __name__ == '__main__':
    main()
