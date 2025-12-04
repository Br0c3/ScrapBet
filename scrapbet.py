import requests 
from bs4 import BeautifulSoup as bfs
import re
from datetime import date
from tabulate import tabulate
import csv
import os


def collect_tr(indice, date=str(date.today())):
    result = requests.get('https://www.bettingclosed.fr/predictions/date-matchs/'+date+'/bet-type/'+indice) 
    print(result)

    soup = bfs(result.text, 'html.parser')
    return soup.find_all(attrs={"classe","rowincontriEven"}) + soup.find_all(attrs={"classe","rowincontriOdd"})
   
def parseMs(soupList):
    r=[["Date et heure"," Region","Equipes","Resultat","Predictions"],]
    for tag in soupList:
        date = tag.find(attrs= {"class","dataMt"}).text
        region = tag.find(attrs= {"class","iconLega"}).img["title"]
        equipes = tag.find(attrs= {"class","matchPhone"}).get_text()
        score = tag.find(attrs= {"class","resultMt" }).text
        pred = tag.find(attrs={"class","predMt"})
        prediction= pred.a.text
        r += [[date,region,equipes,score,prediction],]
    

        #print(date,": ",region,"| ",equipes,"|",score,prediction)
    entete= ["Date et heure"," Region","Equipes","Resultat","Predictions"]
    print(tabulate(r,tablefmt="rounded_grid",maxcolwidths=[None,10,10,10,10], headers=entete))
    return r

def finaltouch():
    print("\n\n**÷÷÷÷÷÷÷SCORE EXACT÷÷÷÷÷÷÷÷÷÷÷÷**")
    yo =collect_tr("correct-scores")
    parseMs(yo)
    print("\n\n**++++++++++++MIXTE+++++++++++++**")
    yo =collect_tr("mixte")
    parseMs(yo)
    print("**\n\n&&&&&&&&&&&&&&& Moins de but / Plus de but &&&&&&&&&&&&&&&**")
    yo= collect_tr("under-over")
    parseMs(yo)
    print("**\n\n€€€€€€€€€€€€€€ BUT/ PAS BUT €€€€€€€€€€€€**")
    yo= collect_tr("gol-nogol")
    parseMs(yo)


def menu():
    while True:
        dictIndice = {"1":"correct-scores","2":"mixte","3":"under-over","4":"gol-nogol"}
        indChoice= input(""" Choisissez l'indice voulu:\n
            1: Score exact
            2: Mixte
            3: Under-Over
            4: But-pas But
            5: Fermer le programme
        >>""")
        if indChoice == "5":
            exit()
        dateChoice = input("Entrez la Date en suivant le format année-mois-jour: ")
        
        result = collect_tr(indice=dictIndice[indChoice],date=dateChoice)
        finRows = parseMs(result)
        dossier = "storage/shared/BackUp-Scrabet"
        if not os.path.exists(dossier):
            os.makedirs(dossier)

        with open(dossier+"/"+dictIndice[indChoice]+dateChoice+".csv", "w",encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(finRows)

menu()

