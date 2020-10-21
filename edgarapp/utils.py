# # -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
import re
from argparse import Namespace

import unicodedata


'''
Table of Contents Extractor


This class takes a filing html file as input and return the table of contents
'''


class TOCAlternativeExtractor(object):
    
    exhibit_end = -1

    def extract(self, url):

        with open(url) as file:
            html = file.read()
        
        self.url = url

        links = self._get_alternative_links(html)

        links += self._get_exhibits(html)

        data = Namespace(table=links)

        return data

    def _get_exhibits(self, html):

        if self.exhibit_end == -1: return ""
        
        html = html.replace( html[:self.exhibit_end], '')

        soup = BeautifulSoup(html, features='lxml')

        exhibits = ""

        for link in soup.find_all('a'):

            link_text = link.get_text()

            if not link_text: continue
                        
            if 'table of content' in link_text.lower(): continue

            href = link.get('href')

            if href:
                exhibits += f"<a href='{href}' class='exhibit-link' target='_blank'>{link_text}</a>"

        if not exhibits:
            return ''

        heading = "<h3 class='exhibit-header'>Exhibits</h3>"

        return heading + exhibits

    def _get_alternative_links(self, html):

        default_table = self._get_toc(html)

        soup = BeautifulSoup(html, 'lxml')
        
        modified_html = html.replace(default_table, '[[REMOVED_TABLE]]')
        modified_soup = BeautifulSoup(modified_html, 'lxml')

        new_soup = ''

        def is_bold(tag):
            
            tag_text = tag.get_text().lower().strip()
            
            if not tag_text:
                return False

            if tag.name == 'a':
                return False

            if not tag.has_attr('style'):
                return False

            style_text = tag.get('style')

            if not ('font-weight:700' in style_text or 'font-weight:bold' in style_text or 'font-weight:800' in style_text or 'font-weight:900' in style_text):
                return False
            
            split_text = tag_text.split()

            if len(split_text) <= 1:
                return False

            if split_text and split_text[0] not in ('item', 'items', 'note', 'part'):
                return False

            if split_text[1] not in ('i', 'i.', 'ii', 'ii.', 'iii', 'iii.', 'iv', 'v', 'vi', 'vii',) and not split_text[1][0].isdigit():
                return False

            return True

        id_counter = 0

        headings = modified_soup.find_all(is_bold)

        num_of_headings = len(list(headings))

        for tag in headings:
            
            tag_text = tag.get_text()

            split_text = tag_text.lower().split()

            if split_text[0] == 'item' and split_text[1][-1] == '.':
                for t in tag.parents:
                    if t.name == 'tr':
                        tag_text = t.get_text()
                        break
                    elif t.name == 'body':
                        break

            tag_first_word = tag_text.split()[0].lower()
            tag_class = tag_first_word if tag_first_word != 'items' else 'item'
            tag_id = tag_first_word + str(id_counter)

            tag['id'] = tag_id

            if tag_first_word == 'part':
                tag_text = tag_text.upper()
            else:
                tag_text = tag_text.title()

            exhbit_text = tag_text.lower().replace('.', ' - ').replace('  ', ' ').strip(' - ')

            if 'exhibit' in exhbit_text and self.exhibit_end == -1:
                self.exhibit_end = html.find(str(tag))

            id_counter += 1

            if id_counter == num_of_headings and self.exhibit_end == -1:
                self.exhibit_end = html.find(str(tag))
            
            new_soup += f"<a href='#{tag_id}' class='{tag_class}-link'>{tag_text}</a>" 

        self.save_html(str(modified_soup.body).replace('[[REMOVED_TABLE]]', default_table).replace('<body>', '').replace('</body>', ''))

        return new_soup

    def _get_toc(self, html):

        text = html

        start = text.index("SECURITIES AND EXCHANGE COMMISSION")

        text = text[start:]

        pattern = re.compile(
            r'<a.+href="([\S]+)".*>Table of Contents.*</a>', re.IGNORECASE)

        links = re.findall(pattern, text)

        pos = -1

        if links:
            links = links[0]

            link = links[links.find('#')+1:]

            pos = text.find(f'id="{link}"')

            if pos == -1:
                pos = text.find(f'name="{link}"')

        if pos == -1:
            pos = text.lower().find("table of contents")

        if pos == -1:
            pos = text.lower().find("index")

        if pos == -1:
            pos = text.lower().find('<hr style="page-break-after:always"')

        text = text[pos:]

        end_pos = text.lower().index('</table>')

        text = text[:end_pos+8]

        self.end_pos = start + len(text)

        return text

    def save_html(self, html):

        with open(self.url, 'w') as file:
            file.write(html)
