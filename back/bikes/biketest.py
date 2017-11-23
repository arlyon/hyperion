import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def get_bikes_request(token: str):
    headers = {
        'cookie': '__cfduid=d307439f96f391d402a004035ea7f1d541509967421; cart_identifier=12857e38cfef8e2a285fb083631511fa; locale=eyJpdiI6Im0rMUtncVI2ZkRKRERoQkhyM2hER2c9PSIsInZhbHVlIjoiYkJGQ1JhdVY5bnBob1BNU21qWnh2QT09IiwibWFjIjoiNDI0M2RmNzNlZTlkMzlkMjc2MzRmNWVlNDJhMWYyYmFlOGZiYWZmNTA3ZTBkODkyNWU5YTk1OWQxMzJjYTg5MSJ9; agreed_cookies=eyJpdiI6InB6aE4raGlucGVMNkd5dWJNVEtHTkE9PSIsInZhbHVlIjoiUWFCck5JejJxSTAzKzhqQUN5ekpxZz09IiwibWFjIjoiNDExMTAxMzZlYjUyOWI5OTY2MDE4YmVmN2NhMTIzZjc4Nzk1ODZkMjBkMTA1YjA3ZDBmODRkYzAxNDg2MDMwOSJ9; _y=B0D47760-1B01-4071-D5A5; _shopify_y=B0D47760-1B01-4071-D5A5; _shopify_fs=2017-11-06T16%3A20%3A31.153Z; __stripe_mid=acb350f6-067a-4599-8eaf-2e4ebde951e4; XSRF-TOKEN=eyJpdiI6IjRsVzF3WGdlQnczVXJzeUVlbEtYTFE9PSIsInZhbHVlIjoibGVNOVBiWW9ZUVVRcGVtcEVEcE95N01VVW9Cd1ZsSmZYVDRLY3RYQ3A5b1wvcUxvUldrb1wvaDhoK2UzS0tFTyt2S1FEK3ZRRWZHYTN2bTg5UmRZZ0xNdz09IiwibWFjIjoiM2M4ZTQxMmFhMjAyZTQxMjQ4YzMwN2Y5ZjZjMDE0ZGM0OTMyYzA4ZmY4YjFlN2Q3NjFkZGE1MWM1MjhlZWY3NyJ9; laravel_session=eyJpdiI6IkZzTDZyNktyQ2QrdnRsQjZOUGxGXC9BPT0iLCJ2YWx1ZSI6ImFwQjI2a0JENW5VM3hHOHB1QU5PVUUrXC80STdNV0dGYzBWMHhKQkhScjNac0gzODRcL245czE3a2EyZ0NmNEN1dmVaNG5mcGV5RlpPOHhMc0F4bDlqcXc9PSIsIm1hYyI6ImUwMTZhMmNlNzhmZDc0NGUzNzZhZGVmMWE2ZDIyMTc4ODYzZmIxYWRiMjY4NTRkYWUwNGY3ODQyMjMyNjkzMjUifQ%3D%3D',
        'origin': 'https://www.bikeregister.com',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,nb;q=0.7,la;q=0.6',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': '*/*',
        'referer': 'https://www.bikeregister.com/stolen-bikes',
        'authority': 'www.bikeregister.com',
        'x-requested-with': 'XMLHttpRequest',
        'dnt': '1',
    }

    data = [
        ('_token', token),
        ('make', ''),
        ('model', ''),
        ('colour', ''),
        ('reporting_period', '1'),
    ]

    request = requests.post('https://www.bikeregister.com/stolen-bikes', headers=headers, data=data)
    return request.json()


def get_token_bs() -> str or None:
    request = requests.get('https://www.bikeregister.com/stolen-bikes')
    soup = BeautifulSoup(request.text, 'html.parser')
    return soup.find(name="_token")


def get_token_selenium() -> str or None:
    """

    async function getData(map, form) {
        form.find('.button').prop('disabled', true).html(button_html + '<i class="fa fa-spinner fa-pulse"></i>');
        $('.toggle-form').html(button_html + '<i class="fa fa-spinner fa-pulse"></i>');

        request = await fetch(form.prop('action'), {
            method: form.find('input[name="_method"]').val() || 'POST',
            body: form.serialize(),
            credentials: "include",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
            },
        })

        return (await (await request).json())
    }

    :return:
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="drivers/chrome_darwin")

    driver.get("https://www.bikeregister.com/stolen-bikes")
    return driver.find_element_by_name("_token")


# data = get_bikes_request(get_token_selenium())
data2 = get_bikes_request(get_token_bs())


print("complete")