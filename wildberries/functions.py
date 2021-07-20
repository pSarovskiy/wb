import time
import uuid

import requests
from PIL import Image
from django.template.defaultfilters import pluralize
from grab import Grab
from resizeimage import resizeimage

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from urllib3.exceptions import MaxRetryError

from product.models import Product, Price

from selenium.webdriver.chrome.options import Options

class Wosminog:
    # options = webdriver.ChromeOptions()
    options = Options()
    chrome_driver = None
    url_list = []
    result = []
    coocies = {'name': 'WILDAUTHNEW_V3',
               'value': 'EFEE4F826EC0238E18B8082E24B1A45067D46E994A93652781D88461AE0C5BC8EBBCB0AD721380C471D9D9C61FC4FA8497B5F30B18CD2C5A96034ABD67A40FF77D7EA5411128E6010BCB69A9DDDC9F3C2DFEE303ABD060B4A67DB953FFC3818FADF1BD68643A5E9B7EC5B855274B68E7ECBF33E37C012D16FC9BF5490E36F185083C0ACFA194196CFE8771A6343C3CA749BE8F716237F4C423B4BE7673ED9F5214D927919B7D238C1989BAA041571A79C61EE580A99D4705A4A9CAB55FE4692C881FFEA515126DF17FC4C10E2C9313A433C4B28872BE01DB29C9DD45C36F75D30E184BC2DD689A91FE78F044529EE82B21B022214795088EAB20F6155F3A2077C1B3A43CB89BFE55687DC5B89DA264C5084A5D5D6EA162068FE81652396587774D0B760D3029307F69BFD776B552BBA9C74138AA064C4FEA6C6B20B9F01698932EA7E8B10389D31AED830F7E60750769B87557B1',
               'domain': '.wildberries.ru'}

    def __init__(self):
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-software-rasterizer')
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--user-data-dir=~/.config/google-chrome')

        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36")
       
        # self.options.add_argument("--remote-debugging-port=9222")

        self.chrome_driver = webdriver.Chrome(executable_path="/usr/local/share/chromedriver", options=self.options)

    def go(self):
        try:
            self.result = []
            if not self.url_list:
                return False
            for i, url in enumerate(self.url_list):
                self.chrome_driver.get(url)
                if i == 0:
                    self.chrome_driver.add_cookie(self.coocies)
                    self.chrome_driver.refresh()
                web_driver_wait = WebDriverWait(self.chrome_driver, timeout=10, poll_frequency=0.5,
                                                ignored_exceptions=[
                                                    NoSuchElementException,
                                                    ElementNotVisibleException,
                                                    ElementNotSelectableException,
                                                    TimeoutException]
                                                )
                web_driver_wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="seller__content"]')))
                self.chrome_driver.find_element(By.TAG_NAME, 'body')
                g = Grab(self.chrome_driver.page_source.encode('utf-8'))
                self.result.append({
                    'url': url,
                    'title': g.doc.select('//meta[@itemprop="name"]').attr('content'),
                    'price': g.doc.select('//meta[@itemprop="price"]').attr('content'),
                    'descr': g.doc.select('//meta[@itemprop="description"]').attr('content', default=''),
                    'image': g.doc.select('//meta[@itemprop="image"]').attr('content', default=''),
                })
                time.sleep(10)
            return self.result
        except TimeoutException or WebDriverException or MaxRetryError as error:
            print(error)
            self.chrome_driver.quit()
        finally:
            self.chrome_driver.quit()


def update_price():
    items = Product.objects.all()
    parser = Wosminog()
    parser.url_list = [item.url for item in items]
    product_data = parser.go()
    update_count = 0
    items_count = len(items)
    for i, item in enumerate(items):
        item_data = product_data[i]

        if item.url != item_data['url']:
            continue

        data_price = float(item_data['price']) or 0
        if item.price != data_price:
            if item.price < data_price:
                item.price_up = True
                item.price_down = False
            elif item.price > data_price:
                item.price_up = False
                item.price_down = True
            item.is_views = True
            item.old_price = item.price
            item.price = data_price
            item.save()
            Price.objects.create(product=item, price=float(item_data['price']))
            update_count += 1
    # send_mess_vk()
    print(f'Провере{pluralize(items_count, "н,ны")} {items_count} това{pluralize(items_count, "p,pов")}')
    print(f'Обновле{pluralize(update_count, "н,ны")} {update_count} това{pluralize(update_count, "р,ров")}')


# def product_data(url):
#     """ Парсит данные продукта """
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument("start-maximized")
#     options.add_argument('--headless')
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                          "Chrome/84.0.4147.125 Safari/537.36")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
#     chrome_driver = webdriver.Chrome(options=options,
#                                      executable_path=r"D:\Myprojects\wildberries\Chromedriver\chromedriver.exe")
#     chrome_driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         "source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """
#     })
#
#     chrome_driver.get(url)
#     chrome_driver.add_cookie({'name': 'WILDAUTHNEW_V3',
#                               'value': 'EFEE4F826EC0238E18B8082E24B1A45067D46E994A93652781D88461AE0C5BC8EBBCB0AD721380C471D9D9C61FC4FA8497B5F30B18CD2C5A96034ABD67A40FF77D7EA5411128E6010BCB69A9DDDC9F3C2DFEE303ABD060B4A67DB953FFC3818FADF1BD68643A5E9B7EC5B855274B68E7ECBF33E37C012D16FC9BF5490E36F185083C0ACFA194196CFE8771A6343C3CA749BE8F716237F4C423B4BE7673ED9F5214D927919B7D238C1989BAA041571A79C61EE580A99D4705A4A9CAB55FE4692C881FFEA515126DF17FC4C10E2C9313A433C4B28872BE01DB29C9DD45C36F75D30E184BC2DD689A91FE78F044529EE82B21B022214795088EAB20F6155F3A2077C1B3A43CB89BFE55687DC5B89DA264C5084A5D5D6EA162068FE81652396587774D0B760D3029307F69BFD776B552BBA9C74138AA064C4FEA6C6B20B9F01698932EA7E8B10389D31AED830F7E60750769B87557B1',
#                               'domain': '.wildberries.ru'})
#     chrome_driver.refresh()
#     try:
#         web_driver_wait = WebDriverWait(chrome_driver, timeout=10, poll_frequency=0.5,
#                                         ignored_exceptions=[
#                                             NoSuchElementException,
#                                             ElementNotVisibleException,
#                                             ElementNotSelectableException,
#                                             TimeoutException]
#                                         )
#         web_driver_wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="seller__content"]')))
#         chrome_driver.find_element(By.TAG_NAME, 'body')
#         g = Grab(chrome_driver.page_source.encode('utf-8'))
#         data = {
#             'url': url,
#             'title': g.doc.select('//meta[@itemprop="name"]').attr('content'),
#             'price': g.doc.select('//meta[@itemprop="price"]').attr('content'),
#             'descr': g.doc.select('//meta[@itemprop="description"]').attr('content', default=''),
#             'image': g.doc.select('//meta[@itemprop="image"]').attr('content', default=''),
#         }
#         return data
#     except TimeoutException or WebDriverException:
#         chrome_driver.refresh()
#         chrome_driver.quit()
#     finally:
#         chrome_driver.refresh()
#         chrome_driver.quit()


def image_upload_path(path):
    """ Загружает изображение и отдает ссылку """
    f = str(path)
    f_ext = f.rsplit('.', 1)[1]  # Расширение загруженного файла
    f_name = str(uuid.uuid4().hex)[:20]  # Имя файла без типа
    thumbs = f'product/{f_name}.{f_ext}'
    if f_ext in ['jpg', 'jpeg', 'png']:
        img = requests.get(f)
        out = open(f'media/{thumbs}', "wb")
        out.write(img.content)
        img.close()
        img = Image.open(f'media/{thumbs}')
        img = resizeimage.resize_cover(img, [200, 200], validate=False)
        img.save(f'media/{thumbs}', optimize=True, quality=80)
        return thumbs


def send_mess_vk():
    import vk_api
    token = "aaec1eff7deb8a4125c2d8f24a9a93b50dfe9ca52207b75189b83bf0e8a8bf0d10d00c54b8502c320371d"
    user_id = 68396673
    vk = vk_api.VkApi(token=token).get_api()
    vk.messages.send(user_id=user_id, message='Привет', random_id=0)
