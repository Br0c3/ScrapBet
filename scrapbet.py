import requests 
from bs4 import BeautifulSoup as bfs
import re
from datetime import date
from tabulate import tabulate
import csv, os
import pandas as pd


def collect_tr(indice, date=str(date.today())):
    try:
        url = f'https://www.bettingclosed.fr/predictions/date-matchs/{date}/bet-type/{indice}'
        result = requests.get(url)
    except:
        print("Erreur de connexion")
        exit()

    soup = bfs(result.text, 'html.parser')
    return soup.find_all(class_="rowincontriEven") + soup.find_all(class_="rowincontriOdd")


def parseMs(indChoice,soupList):
    r=[["Date et heure","Region","Equipes","Resultat","Predictions","Gains ou Perte"]]

    for tag in soupList:
        date = tag.find(class_="dataMt")
        region = tag.find(class_="iconLega")
        equipes = tag.find(class_="matchPhone")
        score = tag.find(class_="resultMt")
        pred = tag.find(class_="predMt")

        date = date.text if date else ""
        try:
          region = region.img["title"] 
        except:
          region = "null"
        equipes = equipes.get_text() if equipes else ""
        score = score.text if score else ""
        prediction = pred.a.text if pred and pred.a else ""

        r.append([date,region,equipes,score,prediction])
        
    (taux, predNum,pourcent,finRows) = caltaux(indChoice,r)
    finRows += [["Taux de reussite",str(taux)+"/"+str(predNum),"En pourcentage (%)", str(pourcent)+" %",""],]
    return r
    
    
def caltaux(choix,table):
    predNum = len(table) - 1
    taux = 0
    for i in table:
        flag = False
        if ( i[0] == "Date et heure"):
            continue
        if (choix == "1"):
            if (i[3].split() == i[4].split()):
                flag = True
            else:
                flag = False
        elif(choix == "3"):
            result = i[3].split("-")

            if result[0] == '' :
                continue
            elif (i[4] == "Under2.5" and int(result[0])+int(result[1]) < 2.5):
                flag = True
            elif (i[4] == "Over2.5" and int(result[0])+int(result[1]) > 2.5):
                flag = True
            else:
                flag = False
        elif (choix == "4"):
            if (i[4] == "Gol" and "0" not in i[3]):
                flag =True
            elif (i[4] == "NoGol" and "0"  in i[3]):
                flag = True
            else: 
                flag = False
        else:
            return 0,0,0,table

        if flag:
            taux += 1
            i.append("V")
        else:
            i.append("X")
            
    return (taux, predNum, format(taux/predNum * 100,".2f"),table)

def checkDate(date):
    
    date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if date_regex.match(date):
        return True
    else:
        return False


def colorset(val):
    return "background-color: green" if val =="V" else ""

def menu():
    while True:
        dictIndice = {"1":"correct-scores","2":"mixte","3":"under-over","4":"gol-nogol","5":"All"}
        indChoice= input(""" Choisissez l'indice voulu:\n
            1: Score exact
            2: Mixte
            3: Under-Over
            4: But-pas But
            5: Toutes les options
            6: Fermer le programme
        >>""")
        if indChoice == "6":
            exit()
        dateChoice = input("Entrez la Date en suivant le format année-mois-jour: ")
        if not checkDate(dateChoice):
            print("Erreur de format de date : Veillez entrer la date au format année-mois-jour")
            continue
        if indChoice == "5" :
          result = list()
          for i in range(1,4):
            result += collect_tr(indice=dictIndice[str(i)],date=    dateChoice)
            finRows = parseMs(str(i),result)
        else:  
          try:
              result = collect_tr(indice=dictIndice[indChoice],date=dateChoice)
              finRows = parseMs(indChoice,result)
          except:
              print("Erreur de choix des options: Veillez choisir parmie les options proposé")
              continue
        
        
        print(finRows)
        entete= ["Date et heure"," Region","Equipes","Resultat","Predi-ctions","Gains ou Perte"]
        print(tabulate(finRows,tablefmt="rounded_grid",maxcolwidths=[10,10,10,8,8,10], headers=entete))
        
        fdata = pd.DataFrame(finRows[1:], columns=finRows[0])

        dossier = "~/storage/shared/BackUp-Scrabet"
        if not os.path.exists(dossier):
            os.makedirs(dossier)
        styled = fdata.style.map(colorset)
        styled.to_excel(dossier+"/"+dictIndice[indChoice]+dateChoice+".xlsx", engine="openpyxl",index=False)
menu()

