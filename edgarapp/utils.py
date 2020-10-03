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

# class TableOfContentsExtractor
class TOCExtractor(object):

    def extract(self, html):
        
        soup = BeautifulSoup(html, features='lxml')

        table =  self._get_toc(soup)

        notes = self._get_notes(soup)
        
        links = self._get_links(table)

        links = links.replace("[ADD_NOTES]", notes, 1)

        data = Namespace(table=links, notes=notes)

        return data

    def _get_notes(self, soup):

        def has_id(tag):
            # TAGS = ("p", "ix:continuation", "ix:nonnumeric")
            TAGS = ("ix:nonnumeric",)
            return tag.name in TAGS  and tag.has_attr("id")
        
        tags = ""

        for tag in soup.find_all(has_id):

            parent_tag = tag.parent
            link_id = None

            match = re.match(r'Note \d+|Item \d+|Part (I|II|V|\d)+', parent_tag.get_text())

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

            if match != None:
                tags += f"<a class='note-link' href='#{link_id}'>{text}</a>"
        
        return tags

    
    def _get_links(self, table_html):

        soup = BeautifulSoup(table_html, features="lxml")

        tags = {}

        for tag in soup.find_all("tr"):

            text = tag.get_text()
            text = unicodedata.normalize("NFKD", text)
            text = re.sub(r'(\d+$)', '', text)

            text = re.sub(r'\\n', '', text)

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

        notes_placeholder = '[ADD_NOTES]'

        for href, text in tags.items():
            
            if not href: continue

            text = text.strip()

            if text.lower().startswith("item"):
                links += f"<a class='item-link' href='{href}'>{text}</a>{notes_placeholder}"
                notes_placeholder = ''

            elif text.lower().startswith("note") or text[0].isdigit():
                links += f"<a class='note-link' href='{href}'>{text}</a>"

            elif text.lower().startswith("consolidated"):
                links += f"<a class='item-link' href='{href}'>{text}</a>"

            else:
                links += f"<a class='part-link' href='{href}'>{text}</a>"
            
        return links

    def _get_toc(self,soup):

        text = str(soup)

        start = text.index("SECURITIES AND EXCHANGE COMMISSION")

        text = text[start:]

        try:
            try:
                pos = text.lower().index("table of contents")
            except:
                pos = text.lower().index("index")
        
        except:
            pos = text.index('<hr style="page-break-after:always"')

        text_info = text[pos:]

        end_pos = text_info.index('</table>')

        needed_text = text_info[:end_pos+8]
        
        return needed_text
