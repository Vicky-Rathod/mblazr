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

    def extract(self, url):

        with open(url) as file:
            html = file.read()
        
        self.url = url

        links = self._get_alternative_links(html)

        links += self._get_exhibits(html)

        data = Namespace(table=links)

        return data

    def _get_exhibits(self, html):

        def is_number_regex(s):
            """ Returns True is string is a number. """
            if re.match("^\d+?\.\d+?$", s) is None:
                return s.isdigit()
            return True

        if self.exhibit_end == -1: return ""
        
        html = html.replace( html[:self.exhibit_end], '')

        soup = BeautifulSoup(html, features='lxml')

        exhibits = ""

        exhibits_dict = {}

        for link in soup.find_all('a'):

            link_text = link.get_text()

            if not link_text: continue
            
            # if is_number_regex(link_text): continue
            
            if 'table of content' in link_text.lower(): continue

            href = link.get('href')

            if href:
                exhibits += f"<a href='{href}' class='exhibit-link' target='_blank'>{link_text}</a>"

        if not exhibits:
            return ''

        heading = "<h3 class='exhibit-header'>Exhibits</h3>"

        return heading + exhibits

    def _get_alternative_links(self, html):

        soup = BeautifulSoup(html, 'lxml')

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

        for tag in soup.find_all(is_bold):
            
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

            if exhbit_text.split()[-1] in ('exhibit', 'exhibit.', 'exhibits', 'exhibits.'):
                # self.exhibit_start, self.exhibit_end = re.search(str(tag),html).span()
                self.exhibit_end = html.find(str(tag))
                print("Git")
            
            id_counter += 1
            
            new_soup += f"<a href='#{tag_id}' class='{tag_class}-link'>{tag_text}</a>" 
        
        self.save_html(str(soup))

        return new_soup

    def save_html(self, html):

        with open(self.url, 'w') as file:
            file.write(html)




class TOCExtractor(object):

    notes_placeholder = '[ADD_NOTES]'
    note_is_set = False

    def extract(self, url):

        with open(url) as file:
            html = file.read()

        notes = self._get_notes(html)

        links = self._get_links(html)

        links = links.replace(self.notes_placeholder, notes, 1)

        links += self._get_exhibits(html)

        data = Namespace(table=links)

        return data

    def _get_notes(self, html):

        self.soup = BeautifulSoup(html, features='lxml')

        def has_id(tag):
            return tag.name in ("ix:nonnumeric",) and tag.has_attr("id")

        tags = ""

        for tag in self.soup.find_all(has_id):

            parent_tag = tag.parent
            link_id = None

            match = re.match(r'Note \d+', parent_tag.get_text())

            if parent_tag.name == 'span' and parent_tag.get_text().lower().startswith('note'):
                text = parent_tag.get_text()
                link_id = parent_tag.get('id')

            else:
                for child in tag.descendants:
                    if child.name == 'span' and child.get_text().lower().startswith('note'):
                        text = child.get_text()
                        link_id = child.get('id')

                        break

            if not link_id:
                link_id = tag.get('id')

            if match:
                tags += f"<a class='note-link' href='#{link_id}'>{text}</a>"

        return tags

    def _get_links(self, html):

        table_html = self._get_toc(html)

        self.table_html = table_html

        soup = BeautifulSoup(table_html, features="lxml")

        del table_html

        tags = {}

        for tag in soup.find_all("tr"):

            text = tag.get_text()
            text = unicodedata.normalize("NFKD", text)
            text = re.sub(r'\s', ' ', text)
            text = re.sub(r'\\n', ' ', text)
            text = text.strip()
            if text.lower().startswith('consolidated') and text.split()[-1].isdigit():

                continue
                # num_to_remove = len(text.split()[-1]) - 4
                # text = text[0:-num_to_remove]
            else:
                text = re.sub(r'(\d+|i+|v+)$', '', text)

            text = re.sub(r'(Item \d+\S*\.)(.*)', '\\1 \\2', text)

            href = None

            for a in tag.descendants:

                try:
                    check = a.get('href')

                    if check:
                        href = check

                        if href not in tags:
                            tags[href] = text

                except:
                    href = None

            if href and href in tags:
                tags[href] = text
            else:
                tags[href] = text

        links = ""

        for href, text in tags.items():

            if not href:
                continue

            text_lower = text.lower()

            if text_lower.startswith("item"):
                if not self.note_is_set:
                    placeholder = self.notes_placeholder
                else:
                    placeholder = ''

                links += f"<a class='item-link' href='{href}'>{text}</a>{placeholder}"
                self.note_is_set = True

            elif text_lower.startswith("notes") or text_lower.startswith("consolidated"):
                links += f"<a class='notes-link' href='{href}'>{text}</a>"

            elif text_lower.startswith("note") or text[0].isdigit():
                links += f"<a class='note-link' href='{href}'>{text}</a>"

            elif text_lower.startswith('part') or text_lower.startswith('signature'):
                links += f"<a class='part-link' href='{href}'>{text}</a>"

            else:
                links += f"<a class='other-link' href='{href}'>{text}</a>"

        return links

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

    def _get_exhibits(self, html):

        def is_number_regex(s):
            """ Returns True is string is a number. """
            if re.match("^\d+?\.\d+?$", s) is None:
                return s.isdigit()
            return True

        try:
            html = html.replace(self.table_html, '')
            exhibit_start_pos = html.lower().index('exhibit')
        except:
            return ''

        html = html.replace(html[:exhibit_start_pos], '')

        soup = BeautifulSoup(html, features='lxml')

        exhibits = ""

        exhibits_dict = {}

        for link in soup.find_all('a'):

            link_text = link.get_text()

            if not link_text:
                continue

            # if is_number_regex(link_text): continue

            if 'table of content' in link_text.lower():
                continue

            href = link.get('href')

            if href and href not in exhibits_dict:
                exhibits_dict[href] = link_text

            elif href:
                exhibits_dict[href] += link_text

        for href, text in exhibits_dict.items():
            exhibits += f"<a href='{href}' class='exhibit-link' target='_blank'>{text}</a>"

        if not exhibits:
            return ''

        heading = "<h3 class='exhibit-header'>Exhibits</h3>"

        return heading + exhibits
