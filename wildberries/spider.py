import time

from django.conf import settings
from grab.spider import Spider, Task
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from product.models import Product


class Wosminog(Spider):
    period_update = 5
    product_list = []

    def create_grab_instance(self, **kwargs):
        """Настраиваем Восминога"""
        grab = super(Wosminog, self).create_grab_instance(**kwargs)
        grab.setup(debug=True, log_file='tmp/log/log.html', debug_post=True, connect_timeout=5, timeout=20, )
        return grab

    def task_generator(self):
        """Генерирует список ссылок на страницы источников"""
        print('∗∗∗ Восминог пошел работать ∗∗∗')
        if len(self.product_list) > 0:
            for el in self.product_list:
                print(f'⋯ получает данные товара со страницы {el}')
                yield Task('product_data', url=el)

    def task_product_data(self, task):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--headless')
        chrome_driver = webdriver.Chrome(options=options,
                                         executable_path=r"D:\Myprojects\Spider\wosminog\chromedriver.exe")
        chrome_driver.get(task.url)
        try:
            product_title = WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '/div[@class="brand-and-name j-product-title"]'))
            )
            return product_title.text()
        finally:
            chrome_driver.close()


if __name__ == '__main__':
    settings.configure()
    bot = Wosminog(thread_number=5, network_service='threaded', grab_transport='pycurl')
    bot.product_list = Product.objects
    print(bot.product_list)
    # bot.run()
    # print(bot.render_stats())
    # print('— — — — — — — — — — — — — — — — — — — —')
    # print(f'Следующая проверка через {bot.period_update} минут')
    # time.sleep(bot.period_update * 60)
    # print('— — — — — — — — — — — — — — — — — — — —')
