import requests


def create_ad():
    response = requests.post('http://127.0.0.1:8085/advertisement/',
                             json={'title': 'nice', 'description': 'ad', 'owner': 1})
    data = response.text
    print(data)


def get_adv():
    response = requests.get('http://127.0.0.1:8085/advertisement/get/4')
    print(response.text)


def get_ads():
    response = requests.get('http://127.0.0.1:8085/advertisements')
    print(response.text)


def patch_adv():
    r = requests.patch('http://127.0.0.1:8085/advertisement/patch/4',
                       json={'title': 'name3'})
    print(r.text)


def delete_adv():
    response = requests.delete('http://127.0.0.1:8085/advertisement/delete/7')
    print(response.text)


get_ads()