from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import codecs
import random
import json
import pprint

def get_data(function, name_page):
    def the_wrapper(function, name_page):
        file = codecs.open(name_page, "r", "utf_8_sig")
        contents = file.read()
        soup = BeautifulSoup(contents, 'lxml')
        result = function(soup)
        file.close()
        return result
    return the_wrapper(function, name_page)


def get_data_wrapper(soup):
    f = soup.find('meta',{'content': 'https://market.yandex.ru'})
    if f:
        all_humans = soup.find_all('div', {'data-zone-name': 'product-review'})
        result = {}
        for i in all_humans:
            name = i.find('div', {'data-zone-name': 'name'})
            reviews = i.find_all('dl')
            if name:
                name = name.string
                result[name] = None
            else:
                name = f"Имя скрыто {random.randint(0, 1000)}"
                result[name] = None
            if len(reviews) > 1:
                result[name] = {}
                for i in reviews:
                    refactor_str = i.text.replace('\r\n', ' ')
                    refactor_str_list = refactor_str.split()
                    key = refactor_str_list[0].replace(':', '')
                    result[name][key] = ' '.join(refactor_str_list[1:len(refactor_str_list)])
            else:
                result[name] = reviews[0].text.replace('\r\n', ' ')
    else:
        all_humans = soup.find_all('div', {'itemprop': 'review'})
        result = {}
        for i in all_humans:
            name = i.find('span', {'itemprop': 'name'})
            review_plus = i.find('div', {'class': 'review-plus'})
            review_minus = i.find('div', {'class': 'review-minus'})
            review_teaser = i.find('div', {'class': 'review-teaser'})
            result[name.text] = {}
            if review_plus:
                result[name.text]['Достоинства'] = review_plus.text
            if review_minus:
                result[name.text]['Недостатки'] = review_minus.text
            if review_teaser:
                result[name.text]['Комментарий'] = review_teaser.text
    return result


app = Flask(__name__)


@app.route('/post', methods=["GET"])
def output_reviews():
    post_name_page = request.args.get('name_page')
    result = get_data(get_data_wrapper, post_name_page)
    pprint.pprint(result)
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    app.run()
