#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 06 16:20:00 2019

@author: Degentleman
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def ConfScrape(conf, season):
    season_id = str(season)
    # specify the url
    conf_page = 'https://www.sports-reference.com/cbb/conferences/{conference}/{season}.html'.format(conference=conf, season=season_id)
    # query the website and return the html to the variable ‘page’
    conf_html = urlopen(conf_page)
    conf_soup = BeautifulSoup(conf_html, 'html.parser')
    cs = conf_soup
    schools = cs.findAll('td', attrs={'data-stat':'school_name'})
    links = [td.a['href'] for td in schools]
    school_list = []
    for link in links:
        name = link[13:]
        del_index = name.index('/2019.html')
        team_name = name[0:del_index]
        school_list.append(team_name)
    schools_in_conf = pd.DataFrame(data=school_list, columns=['School_ID'])
    return(schools_in_conf)
    
def SchoolScrape(school, season):
    school_id = str(school)
    season_id = str(season)
    # specify the url
    team_page = 'https://www.sports-reference.com/cbb/schools/{school}/{season}-schedule.html'.format(school=school_id,season=season_id)
    # query the website and return the html to the variable ‘page’
    html = urlopen(team_page)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.findAll('div', attrs={'id':'all_schedule'})
    data_rows = table[0].select('tr')
    headers = [th.text for th in data_rows[0].findAll('th')]
    headers[4] = 'Site'
    headers[7] = 'Result'
    dataset = []
    for row in data_rows[1:]:
        data = row.findAll(['th', 'td'])
        row_data = [cell.text for cell in data]
        dataset.append(row_data)
    results_df = pd.DataFrame(data=dataset, columns=headers)
    teamDF = results_df
    teamDF.Site = teamDF.Site.str.replace('N', 'Neutral')
    teamDF.Site = teamDF.Site.str.replace('@', 'Away')
    teamDF.Result = teamDF.Result.str.replace('W', 'Win')
    teamDF.Result = teamDF.Result.str.replace('L', 'Loss')
    return(teamDF)
# Get the url abbreviation codes for each conference
NCAAB_CONF = pd.read_csv('NCAA Conferences - Database.csv', delimiter=",").fillna('')
keys = list(NCAAB_CONF.Conf_Key)

#Input School and Conference and Season
conference = keys[22]
season = '2019'
SS = SchoolScrape
CS = ConfScrape
schools = list(CS(conference, season).School_ID)
CONF_DF = pd.DataFrame()
for school in schools:
    teamDF = SS(school,season)
    teamDF = teamDF[(teamDF.G != 'G')].reset_index(drop=True)
    spread = pd.Series(data=np.array(pd.to_numeric(teamDF.Tm),dtype=int)-np.array(pd.to_numeric(teamDF.Opp),dtype=int), name='Spread')
    total = pd.Series(data=np.array(pd.to_numeric(teamDF.Tm),dtype=int)+np.array(pd.to_numeric(teamDF.Opp),dtype=int), name='Total')
    DF = pd.concat([teamDF[list(teamDF)[0:10]], total, spread, teamDF[list(teamDF)[10:]]],axis=1)
    CONF_DF = pd.concat([CONF_DF,DF],axis=0)
    filename = conference+str('-results.csv')
    CONF_DF.to_csv(filename)