from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json
import treelib
from treelib import Node, Tree

class ITSM_Crawler():
    USERNAME = "kc.suen@towngas.com"
    PASSWORD = "Y5837810y!"

    LOGIN_URL = "https://adfs.sts.towngas.com/adfs/ls/?wa=wsignin1.0&wtrealm=https%3a%2f%2fitsm.towngas.com%2f&wctx=rm%3d0%26id%3dpassive%26ru%3d%252f&wct=2018-07-10T08%3a29%3a29Z"
    HOMEPAGE = "homepage"
    URL_PREFIX = "https://itsm.towngas.com/"

    browser = None
    ITSM_Tree = None

    def __init__(self):
        self.array = []
        self.ITSM_Tree = Tree()
        self.ITSM_Tree.create_node("Homepage", "homepage", data=self.URL_PREFIX)
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": "./",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.browser = webdriver.Chrome(chrome_options=options)

    def login(self):
        self.browser.get(self.LOGIN_URL)
        username = self.browser.find_element_by_id('userNameInput')
        username.send_keys(self.USERNAME)
        password = self.browser.find_element_by_id('passwordInput')
        password.send_keys(self.PASSWORD)
        self.browser.find_element_by_id('submitButton').click()
        html = self.browser.page_source
        return html

    def get_HTML_From_URL(self, url):
        print("Accessing " + str(url))
        self.browser.get(url)
        html = self.browser.page_source
        return html

    def getMenu(self, soup):
        menu_item_array = soup.findAll(class_="inner_div")
        for menu_item in menu_item_array:
            link_tag = menu_item.find('a', href=True)
            img_tag = menu_item.find('img', title=True)
            if(link_tag != None and img_tag != None):
                title = img_tag.get('title')
                _id = title.lower()
                link = self.URL_PREFIX + link_tag.get('href')
                self.ITSM_Tree.create_node(title, _id, data=link, parent=self.HOMEPAGE)
                html_to_parse = self.get_HTML_From_URL(link)
                soup = BeautifulSoup(html_to_parse, "lxml")
                self.getMenuContent(soup, _id)

    def getMenuContent(self, soup, _parent):
        menu_content_array = soup.findAll(class_="cboxlist")
        for menu_content in menu_content_array:
            print(menu_content)
            id_onclick = menu_content.get('id')
            print(id_onclick)
            title = menu_content.find(class_='boxtitle').get_text()
            pre_link = self.browser.current_url
            self.browser.find_element_by_id(id_onclick).click()
            link = self.browser.current_url
            print(title)
            print(link)
            self.ITSM_Tree.create_node(title, title.lower(), data=link, parent=_parent)
            self.browser.get(pre_link)

    def main(self):
        _html = self.login()
        soup = BeautifulSoup(_html, "lxml")
        self.getMenu(soup)
        self.ITSM_Tree.show()
        print(self.ITSM_Tree.to_json(with_data=True))

if __name__ == "__main__":
    crawler = ITSM_Crawler()
    crawler.main()
    crawler.browser.close()