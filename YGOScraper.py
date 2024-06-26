from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

def get_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    cards = soup.find_all("div", class_="t_row c_normal")

    data=[]

    #item[CardName, CardType, SubType, Attribute, Types, Level, Link, Pendulum, ATK, DEF, Description, Passcode]
    
    for card in cards:
        item={}
        item["CardName"]= card.find("span", class_="card_name").text
        match card.find("span", class_="box_card_attribute").find("span").text:
            case "SPELL":
                item["CardType"]="Spell"
                tempSubType=card.find("span", class_="box_card_effect")
                if tempSubType != None:
                    item["SubType"]=card.find("span", class_="box_card_effect").find("span").text
                else:
                    item["SubType"]=-1
                item["Attribute"]=-1
                item["Types"]=-1
                item["Level"]=-1
                item["Link"]=-1
                item["Pendulum"]=-1
                item["ATK"]=-1
                item["DEF"]=-1
                item["Pendulum Description"]=-1
                Desc = card.find("dd", class_="box_card_text c_text flex_1").text
                while Desc[0].isspace():
                    Desc = Desc[1:]
                while Desc[-1].isspace():
                    Desc = Desc[:-1]
                item["Description"]=Desc
            case "TRAP":
                item["CardType"]="Trap"
                tempSubType=card.find("span", class_="box_card_effect")
                if tempSubType != None:
                    item["SubType"]=card.find("span", class_="box_card_effect").find("span").text
                else:
                    item["SubType"]=-1
                item["Attribute"]=-1
                item["Types"]=-1
                item["Level"]=-1
                item["Link"]=-1
                item["Pendulum"]=-1
                item["ATK"]=-1
                item["DEF"]=-1
                item["Pendulum Description"]=-1
                Desc = card.find("dd", class_="box_card_text c_text flex_1").text
                while Desc[0].isspace():
                    Desc = Desc[1:]
                while Desc[-1].isspace():
                    Desc = Desc[:-1]
                item["Description"]=Desc
            case default:                   #Monsters
                item["CardType"]="Monster"
                item["SubType"]=-1
                item["Attribute"]=card.find("span", class_="box_card_attribute").find("span").text
                TypesList=card.find("span", class_="card_info_species_and_other_item").text.strip()
                item["Types"]=TypesList[1:-1]
                if card.find("span", class_="box_card_level_rank level") != None:
                    LevelRank=card.find("span", class_="box_card_level_rank level").find("span").text.split()
                    item["Level"]=LevelRank[1]
                else:
                    item["Level"]=-1
                if card.find("span", class_="box_card_linkmarker") != None:
                    Link=card.find("span", class_="box_card_linkmarker").find("span").text.split()
                    item["Link"]=Link[1]
                else:
                    item["Link"]=-1
                if card.find("span", class_="box_card_pen_scale") != None:
                    PendScale=card.find("span", class_="box_card_pen_scale").text.split()
                    item["Pendulum"]=PendScale[2]
                    brTemp=card.find("span", class_="box_card_pen_effect c_text flex_1").select("br")
                    if card.find("span", class_="box_card_pen_effect c_text flex_1").find("br"):
                        brTemp[0].replace_with("\n")
                    PendDesc = ""
                    PendDesc = card.find("span", class_="box_card_pen_effect c_text flex_1").text
                    if len(PendDesc) > 1:
                        while PendDesc[0].isspace():
                            PendDesc = PendDesc[1:]
                        while PendDesc[-1].isspace():
                            PendDesc = PendDesc[:-1]
                        item["Pendulum Description"]=PendDesc
                    else:
                        item["Pendulum Description"]=""
                else:
                    item["Pendulum"]=-1
                    item["Pendulum Description"]=-1
                item["ATK"]=card.find("span", class_="atk_power").find("span").text.split()[1]
                item["DEF"]=card.find("span", class_="def_power").find("span").text.split()[1]
                brTemp=card.find("dd", class_="box_card_text c_text flex_1").select("br")
                if card.find("dd", class_="box_card_text c_text flex_1").find("br"):
                    brTemp[0].replace_with("\n")
                Desc = card.find("dd", class_="box_card_text c_text flex_1").text
                while Desc[0].isspace():
                    Desc = Desc[1:]
                while Desc[-1].isspace():
                    Desc = Desc[:-1]
                item["Description"]=Desc

        cardIdLinkPrefix = "https://yugioh.fandom.com/wiki/"
        if item["CardName"].find("(Updated") != -1:
            nameParts = item["CardName"].split(" ")
            item["CardName"] = ""
            notDone = 1
            for part in nameParts:
                if(part != "(Updated" and notDone):
                    item["CardName"] += part + " "
                else:
                    notDone = 0
        cardName = item["CardName"].replace(" ", "_").replace("?", "%3F").replace("#", "")
        pageRes = requests.get(cardIdLinkPrefix + cardName).text
        pageResSoup = BeautifulSoup(pageRes, "lxml")
        keyElTable = pageResSoup.find("table", class_ = "cardtable")
        keyElProperty = pageResSoup.find("a", title = "Property:Passcode")
        keyEl = None
        problemID = ""
        if keyElProperty != None:
            keyEl = keyElProperty.find_parent().find_next_sibling()
        else:
            problemID = "No cardtable"
        key = ""
        if keyEl != None:
            temp = re.findall('[0-9]+', keyEl.text)
            key = temp[0]
        else:
            problemID += " No <a class=new>"
            if keyElTable != None:
                keyEl = keyElTable.find("a", class_ = "mw-redirect")
            if keyEl != None:
                key = keyEl.text
            else:
                problemID += " No <a class=mw-redirect>"
        

        if key == "" or not key.isnumeric():
            pageRes = requests.get(cardIdLinkPrefix + cardName + "_(card)").text
            pageResSoup = BeautifulSoup(pageRes, "lxml")
            keyElTable = pageResSoup.find("table", class_ = "cardtable")
            keyElProperty = pageResSoup.find("a", title = "Property:Passcode")
            keyEl = None
            if keyElProperty != None:
                keyEl = keyElProperty.find_parent().find_next_sibling()
            else:
                problemID += " No cardtable"
            key = ""
            if keyEl != None:
                temp = re.findall('[0-9]+', keyEl.text)
                key = temp[0]
            else:
                if keyElTable != None:
                    keyEl = keyElTable.find("a", class_ = "mw-redirect")
                if keyEl != None:
                    key = keyEl.text
            with open('Unsuccessful.txt', 'a', encoding="utf-8") as f:
                f.write("Can't find id for " +str(cardName) + "\nProblem Location" + str(problemID) + "\n")
        if key.isnumeric():
            while key[0] == '0':
                key = key[1:] 
            item["Passcode"] = key
            CardLinkPrefix = "https://images.ygoprodeck.com/images/cards/"
            src = CardLinkPrefix + key + ".jpg"
            item["CardImage"] = src
            r = requests.get(src)
            open(item["Passcode"] + ".jpg", 'wb').write(r.content)
        else:
            with open('Unsuccessful.txt', 'a', encoding="utf-8") as f:
                problemID = "Not numeric"
                f.write("Can't find id for " +str(cardName) + "\nProblem Location " + str(problemID) + ": " + key + "\n")

        data.append(item)
    return data

def export_data(data):
    df = pd.DataFrame(data)
    df.to_excel("YGO_Cards_DB.xlsx")
    df.to_csv("YGO_Cards_DB.csv")

if __name__ == '__main__':
    data = get_data("https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sess=1&page=1&mode=1&stype=1&link_m=2&othercon=2&sort=1&rp=100")
    for i in range(2, 140):
        linkText = "https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=1&sess=1&page=" + str(i) + "&mode=1&stype=1&link_m=2&othercon=2&sort=1&rp=100"
        data += get_data(linkText)
    export_data(data)
    print("Done.")