# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
import re
from argparse import Namespace

import unicodedata

'''
Table of Contents Extractor


This class takes a filing html file as input and return the table of contents
'''


class TOCExtractor(object):

    notes_placeholder = '[ADD_NOTES]'
    note_is_set = False

    def extract(self, html):

        notes = self._get_notes(html)
        
        links = self._get_links(html)

        links = links.replace(self.notes_placeholder, notes, 1)

        links += self._get_exhibits(html)

        data = Namespace(table=links)

        return data

    def _get_notes(self, html):

        self.soup = BeautifulSoup(html, features='lxml')

        def has_id(tag):
            return tag.name in ("ix:nonnumeric",)  and tag.has_attr("id")
        
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
            text = re.sub(r'(\d+|i+|v+)$', '', text)

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
            
            if not href: continue

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

            elif text_lower.startswith('part'):
                links += f"<a class='part-link' href='{href}'>{text}</a>"
            
            else:
                links += f"<a class='other-link' href='{href}'>{text}</a>"
 
        return links

    def _get_toc(self,html):

        text = html

        start = text.index("SECURITIES AND EXCHANGE COMMISSION")

        text = text[start:]

        try:
            try:
                pos = text.lower().index("table of contents")
            except:
                pos = text.lower().index("index")
        
        except:
            pos = text.index('<hr style="page-break-after:always"')

        text = text[pos:]

        end_pos = text.index('</table>')

        text = text[:end_pos+8]

        self.end_pos = start + len(text)
        
        return text

    def _get_exhibits(self, html):

        def is_number_regex(s):
            """ Returns True is string is a number. """
            if re.match("^\d+?\.\d+?$", s) is None:
                return s.isdigit()
            return True
        
        html = html.replace(self.table_html, '')

        html = html.replace(
            html[:html.index('exhibit')], '')

        soup = BeautifulSoup(html, features='lxml')

        exhibits = "<h5 class='exhibit-header'>Exhibits</h5>"

        for link in soup.find_all('a'):
            if is_number_regex(link.get_text()): continue
            exhibits += f"<a href='{link.get('href')}' class='exhibit-link' target='_blank'>{link.get_text()}</a>"

        return exhibits
