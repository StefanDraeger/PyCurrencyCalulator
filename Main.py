from flask import Flask, render_template, request
import calendar
import requests
from bs4 import BeautifulSoup
import lxml
import datetime
from pickle import TRUE, NONE

app = Flask(__name__, static_url_path='/static')


class Currency:

    def __init__(self, month, year, iso3, value):
        self.month = int(month)
        self.year = int(year)
        self.iso3 = str(iso3)
        self.value = float(value)

        
historyCurrencys = []; 

currencyConversion = {
    "EUR-USD":1.1916,
    "USD-EUR":0.8392,
    "date":"-undefined-"
    }

currencys = {
    "EUR": {
        "text":"Euro",
        "sign":"\u20ac",
        "iso2code":"EU",
        "iso3code": "EUR"
        },
    "USD": {
        "text":"Dollar",
        "sign":"$",
        "iso2code":"US",
        "iso3code":"USD"
        }        
    }

currentYear = 0
currentMonth = 0


@app.route('/')
def start():
    global currentYear
    global currentMonth
    
    currentYear = datetime.date.today().year 
    currentMonth = datetime.date.today().month
    currentDateStr = getFormatedDate(currentMonth, currentYear)
    iso3 = currencys["USD"]["iso3code"]
    if historyListContainsElement(currentMonth, currentYear, iso3):
        usDollar = findHistoryElement(currentMonth, currentYear, iso3)
    else:
        usDollar = loadDataFromCustoms(currencys["USD"]["iso2code"], currentMonth, currentYear)
        appendHistoryData(currentMonth, currentYear, iso3, usDollar)

    euro = round(1 / usDollar, 4)
    
    currencyConversion["EUR-USD"] = usDollar
    currencyConversion["USD-EUR"] = euro
    currencyConversion["date"] = currentDateStr
    
    srcValue = '1'
    srcCurrency = currencys['EUR']
    destCurrency = currencys['USD']
    
    return render_template("template.html", umrechnunskurse=currencyConversion , srcValue=srcValue, srcCurrencyBlock=srcCurrency, destCurrencyBlock=destCurrency, historyCurrencys=historyCurrencys)


def getFormatedDate(month, year):
    date = "01."
    if(month < 10):
        date = date + "0"
    date = date + str(month) + "." + str(year)
    return date


@app.route('/calc')
def calcCurrency():
    srcValue = request.args.get("srcValue")
    srcCurrency = request.args.get("srcCurrency")
    destCurrency = request.args.get("destCurrency")
    key = srcCurrency + "-" + destCurrency
    rate = currencyConversion[key]
    
    value = float(srcValue.replace(",", "."))
    output = round(value * rate, 2)
    
    return render_template("output.html", umrechnunskurse=currencyConversion , srcValue=srcValue, destOutput=str(output), srcCurrencyBlock=currencys[srcCurrency], destCurrencyBlock=currencys[destCurrency], historyCurrencys=historyCurrencys)


def loadDataFromCustoms(currency, monat, jahr): 
    max_day_in_month = calendar.monthrange(jahr, monat)[1]

    url = "http://www.zoll.de/SiteGlobals/Functions/Kurse/KursExport.xml?"\
    +"view=xmlexportkursesearchresultZOLLWeb&kursart=1&iso2code2=" + currency\
    +"&startdatum_tag2=01&startdatum_monat2=" + str(monat) + "&startdatum_jahr2=" + str(jahr)\
    +"&enddatum_tag2=" + str(max_day_in_month) + "&enddatum_monat2=" + str(monat) + "&enddatum_jahr2="\
    +str(jahr) + "&sort=asc&spalte=gueltigkeit"

    print(url)

    r = requests.get(url)
    document = BeautifulSoup(r.content, "lxml")
    return float(document.find('kurswert').text.replace(",", "."))

def historyListContainsElement(month, year, iso3):
    return findHistoryElement(month, year, iso3) != None

def findHistoryElement(month, year, iso3):
    for c in historyCurrencys:
        if c.month == month and c.year == year and c.iso3 == iso3:
            return c
        return None

def appendHistoryData(month, year, iso3, value):
    isNew = True
    for c in historyCurrencys:
        if c.month == month and c.year == year:
            isNew = False
            print(c)
            break;
        
    if isNew:
        historyCurrencys.append(Currency(month, year, iso3, value))
        with open("static/data.csv", "a") as file:
            file.write(str(month) +';' + str(year) + ';' + str(iso3) + ';' + str(value))

def loadData():
    global historyCurrencys
    with open("static/data.csv", "r") as file:
        for line in file:
            values = line.strip().split(";")
            print(values)
            if(len(values) == 4):
                historyCurrencys.append(Currency(values[0], values[1], values[2], values[3]))
    
    year = datetime.date.today().year 
    month = datetime.date.today().month
    iso3 = currencys["USD"]["iso3code"]
    if historyListContainsElement(month, year, iso3):
        iso2 = currencys["USD"]["iso2code"]
        value = loadDataFromCustoms(iso2, month, year)
        appendHistoryData(month, year, iso3, value)
    
app.before_first_request(loadData);    

if __name__ == '__main__':
    app.run()
    
