from bs4 import BeautifulSoup # Recherche simplifié à travers du code HTML
import requests # Requêtes HTTPS
import re # Expression régulière
import json # Manipulation de données JSON
from tqdm import tqdm # Barre de progression UI
import pandas as pd # Stockage de données dans un panda's dataframe

prefix_URL = 'https://www.saq.com/fr/produits/spiritueux/gin?availability=Include+the+products+that+are+not+available&p='
suffix_URL = '&pays_origine=Canada&product_list_limit=96&product_list_order=name_asc'
product_URL = 'https://www.saq.com/fr/'

# Initialisation des variables
liste_gins = pd.DataFrame(index=range(500),columns=['id','name','price','URL'])
x = 0

for page in range(1,3):
    try:
        response = requests.get(prefix_URL + str(page) + suffix_URL)
    except:
        break
        print(f"Le nombre de pages final est {page}")

    print(f"Nous sommes à la page {page}")

    # Retour du code html de la page
    html = response.text

    # Extraction de l'information pertinente
    soup = BeautifulSoup(html, 'html.parser')
    pretty = soup.prettify()
    yes = soup.find_all(string=re.compile("staticImpressions"))
    
    # Nettoyage du texte et conversion en dictionnaire Python
    yes = str(yes)
    yes = yes[143:-378]
    ouioui = chr(92) + chr(110) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32) + chr(32)
    oui = yes.replace(ouioui,'')
    oui = oui.replace(chr(32),'')
    oui = oui.replace(",",",\n")
    oui = '{\n"data":[\n' + oui + '\n]\n}'
    oui = re.sub(r':(?=\d)+',':"',oui)
    oui = re.sub(r'(\d+)\,','1",',oui)
    
    # Criss de unicode à marde
    oui = oui.replace(r'\\u0020',' ')
    oui = oui.replace(r'\\u0023','#')
    oui = oui.replace(r'\\u002D','-')
    oui = oui.replace(r'\\u00E9','é')
    oui = oui.replace(r'\\u00C9','É')
    oui = oui.replace(r'\\u0027',chr(39))
    oui = oui.replace(r'\\u0026','&')
    oui = oui.replace(r'\\u00E8','è')
    oui = oui.replace(r'\\u0021','!')
    oui = oui.replace(r'\\u00FB','û')
    oui = oui.replace(r'\\u00EA','ê')
    oui = oui.replace(r'\\u00B0','°')
    oui = oui.replace(r'\\u00E0','à')
    oui = oui.replace(r'\\u00F4','ô')
    
    final = json.loads(oui, strict=False)

    # Convertion d'un dictionnaire de dictionnaires en DataFrame
    for i in tqdm(final['data']):
        for key, value in i.items():
            if key == 'id':
                id_data = value
            elif key == 'name':
                name = value
            elif key == 'price':
                price = value
        liste_gins.loc[x] = id_data,name,price,product_URL+id_data
        x += 1

# Formatting des nouvelles données et de celles en csv
liste_gins = liste_gins.dropna()
liste_gins['id'] = pd.to_numeric(liste_gins['id'])
liste_gins['price'] = pd.to_numeric(liste_gins['price'])
loaded_data = pd.read_csv('gins.csv')
loaded_data['id'] = pd.to_numeric(loaded_data['id'])

# Extraction des nouveaux gins
nouveau_gin = liste_gins.append(loaded_data)
nouveau_gin = nouveau_gin.drop_duplicates(keep=False).reset_index(drop=True)

# Enregistrement des changements pour la prochaine exécution
liste_gins.to_csv('gins.csv', encoding='utf-8', index=False)

# Envoi d'alertes
## Message messenger par API Facebook ?
## SMS ?
## Email ?



