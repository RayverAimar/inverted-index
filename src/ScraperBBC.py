from bs4 import BeautifulSoup
import requests
import json
import time
from settings import USER_AGENT



ACCEPTED = 200

class BBCScraper:
    def __init__(self) -> None:
        self.__url = "https://www.bbc.com"

    def get_soup(self, url, parser='lxml'):
        headers = {'User-Agent' : USER_AGENT}
        response = requests.get(url, headers=headers)
        if response.status_code != ACCEPTED:
            return None
        soup = BeautifulSoup(response.text, parser)
        return soup
    
    def get_hot_topics_links(self, hot_sections):
        links = []
        for section in hot_sections:
            if section.a:
                hot_topic_title = section.a.span.get_text()
                if hot_topic_title == 'Video':
                    continue
                hot_topic_url = self.__url + section.a.get('href')
                links.append(hot_topic_url)
        return links

    def get_note(self, soup):
        note_dict = {}
        title = soup.find('h1').get_text()
        subtitle = soup.find('div', attrs={'data-component':'text-block'}).get_text()
        paragraphs = soup.find_all('div', attrs={'data-component':'text-block'})[1:-3]
        content = ""
        for paragraph in paragraphs:
            content += paragraph.get_text()
        if not content:
            raise AttributeError()
        note_dict['title'] = title
        note_dict['subtitle'] = subtitle
        note_dict['content'] = content
        return note_dict
        
    def get_notes_links(self, soup):
        links = []
        links.append(self.__url + soup.find('a', attrs={'class':'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-paragon-bold gs-u-mt+ nw-o-link-split__anchor'}).get('href'))
        rest_notes_links = soup.find_all('a', attrs={'class':'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor'})
        for note_link in rest_notes_links:
            links.append(self.__url + note_link.get('href'))
        return links

    def get(self):
        soup : BeautifulSoup = self.get_soup(self.__url + '/news')
        hot_sections : list[BeautifulSoup] = soup.find('ul', attrs={'class':'nw-c-nav__wide-sections'}).find_all('li')[1:-4]
        hot_topics_links = self.get_hot_topics_links(hot_sections)
        start = time.time()
        for topic_link in hot_topics_links:
            try:
                print("[TOPIC_LINK]", topic_link)
                soup = self.get_soup(topic_link)
                notes_links = self.get_notes_links(soup)
                for note_link in notes_links:
                    note_soup = self.get_soup(note_link)
                    if not note_soup:
                        continue
                    note_id = note_link.split('/')[-1]
                    note_dict = self.get_note(note_soup)
                    if note_dict:
                        with open('../docs/' + note_id + '.json', "w") as json_file:
                            json.dump(note_dict, json_file)
            except AttributeError:
                continue
            except requests.ConnectionError:
                continue
        end = time.time()
        print(end - start)


myScraper = BBCScraper()
#soup = myScraper.get_soup("https://www.bbc.com/sport/football/66637879")
#myScraper.get_note(soup)
myScraper.get()