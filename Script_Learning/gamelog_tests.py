from bs4 import BeautifulSoup
import pandas as pd
from xml.dom.minidom import parse
with open('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\131921_Japan_NorwayGamelog.xml') as fp:
    data = BeautifulSoup(fp, 'xml')

home_teams = data.find('Rosters').find('HomeTeam')
home_id = home_teams['TeamId']
players = home_teams.find_all('Player')
jNum = [x.find('Number').text for x in players]
pId = [x.find('PlId').text for x in players]

dict_fifa = dict(zip(jNum, pId))

dfb_ids = pd.read_csv('C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Players + teams.xlsx - Tabelle1.csv')
home_dfb = dfb_ids.loc[dfb_ids['Team ID IFES'] == int(home_id)]
jNum_dfb = home_dfb['Rückennummer'].tolist()
pId_dfb = home_dfb['Spieler ID D3'].tolist()

dict_dfb = dict(zip(jNum_dfb, pId_dfb))

new_dict = {}

for jNumber in dict_fifa:
    new_id = str(dict_dfb[float(jNumber)])
    new_dict.update({str(jNumber): new_id})


# Testing with minidom
gamelog_path = 'C:\\Users\\a.banning\\PycharmProjects\\Work_Tracab\\131921_Japan_NorwayGamelog.xml'
xml_doc = parse(gamelog_path)
element = xml_doc.getElementsByTagName('TracabData')[0]
d = dict(element.attributes.items())

home = xml_doc.getElementsByTagName('HomeTeam')[0]
players = home.childNodes
id_elements = [x.setAttribute('PlId', 'test')for x in xml_doc.getElementsByTagName('HomeTeam')[0].childNodes]

for i in players:
    i.getElementsByTagName('PlId')[0].firstChild.data = 8
ids = [x.getElementsByTagName('PlId')[0].firstChild.data for x in players]

xml_doc.writexml(open('data.xml', 'w'),
               indent="  ",
               addindent="  ",
               newl='\n')