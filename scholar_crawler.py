# -*- coding: utf-8 -*-

from requests import get
from bs4 import BeautifulSoup
import numpy as np
from time import sleep
import pandas as pd

url = 'https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:reinforcement_learning'
base_url = 'https://scholar.google.com'
base_page_url = url + '&after_author='

def page_parse(html_soup):

    # FIND AUTHOR LIST AND CITATION NUMBERS #
    authors = html_soup.find_all('div', class_ = 'gsc_1usr gs_scl')
    ind = 0
    author_list = []
    link_list = []
    citation_list = []

    while ind < len(authors):
        link_list.append(authors[ind].a['href'])
        author_list.append(authors[ind].a.text.lower())

        cited_string = authors[ind].find('div', class_='gsc_oai_cby').text
        cited_num = int(cited_string.split()[2])
        citation_list.append(cited_num)

        ind += 1


    # FIND INSTITUTION LIST #
    institution_list = []

    for link in link_list:
        link_response = get(base_url + link)
        link_soup = BeautifulSoup(link_response.text, 'html.parser')

        institution_html = link_soup.find('div', class_ = 'gsc_prf_il')

        if institution_html.a is None:
            institution_list.append('0')
        else:
            institution_list.append(institution_html.a.text.lower())


    # FIND THE NEXT PAGE URL #
    next_page_list = []
    button = html_soup.find('button', class_ = 'gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx')
    button_text = button['onclick']

    count = 0
    for let in button_text[::-1]:
        if let == "\\":
            count += 1
        if count == 2 and let != "\\":
            next_page_list.append(let)

    next_page = ''.join(next_page_list)[::-1][3:]

    return author_list, citation_list, institution_list, next_page



if __name__ == "__main__":
    df = pd.DataFrame(columns=['Authors', 'Citations', 'Institutions'])
    page = 0
    npages = 100
    turl = url

    while page < npages:
        html_soup = BeautifulSoup(get(turl).text, 'html.parser')
        author_list, citation_list, institution_list, next_page = page_parse(html_soup)

        df_temp = pd.DataFrame({
        'Authors': author_list,
        'Citations': citation_list,
        'Institutions': institution_list,
        })

        df = df.append(df_temp, ignore_index=True)

        turl = base_page_url + next_page

        page += 1

        if page%10 == 0:
            df.to_csv('schools.csv', encoding='utf-8')
            print("On page ", page)

    # Hard coded for top authors that do not list their institution on google scholar.
    df.loc[df['Authors'] == 'richard s. sutton', 'Institutions'] = 'university of alberta'
    df.loc[df['Authors'] == 'sean meyn', 'Institutions'] = 'university of florida'
    df.loc[df['Authors'] == 'nowe ann', 'Institutions'] = 'vrije universiteit brussel'
    df.loc[df['Authors'] == 'michael bowling', 'Institutions'] = 'university of alberta'
    df.loc[df['Authors'] == 'jan gläscher', 'Institutions'] = 'university of hamburg'
    df.loc[df['Authors'] == 'Xuejun Liao', 'Institutions'] = 'duke university'

    data_clean = df.loc[(df['Institutions'] != '0')]

    data_clean = data_clean.replace('brown', 'brown university')
    data_clean = data_clean.replace('university of california at berkeley', 'uc berkeley')
    data_clean = data_clean.replace('university of california, berkeley', 'uc berkeley')
    data_clean = data_clean.replace('carnegie mellon', 'carnegie mellon university')

    data_clean.to_csv('schools_clean.csv', encoding='utf-8')
