from flask import Flask, render_template, request
import calendar
import requests
from bs4 import BeautifulSoup
import lxml
import datetime

app = Flask(__name__)

currencyConversion = {
    "EUR-USD":1.1916,
    "USD-EUR":0.8392,
    "date":"-undefined-"
    }

currencys = {
    "EUR": {
        "text":"Euro",
        "sign":"\u20ac",
        "iso2code":"EU"
        },
    "USD": {
        "text":"Dollar",
        "sign":"$",
        "iso2code":"US"
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
    
    usDollar = loadDataFromCustoms(currencys["USD"]["iso2code"], currentMonth, currentYear)
    euro = round(1/usDollar,4)
    
    currencyConversion["EUR-USD"] = usDollar
    currencyConversion["USD-EUR"] = euro
    currencyConversion["date"] = currentDateStr
    
    srcValue = '1'
    srcCurrency = currencys['EUR']
    destCurrency = currencys['USD']
    
    return render_template("template.html", umrechnunskurse=currencyConversion , srcValue=srcValue, srcCurrencyBlock=srcCurrency, destCurrencyBlock=destCurrency)

def getFormatedDate(month, year):
    date = "01."
    if(month< 10):
        date = date + "0"
    date = date + str(month)+"." +str(year)
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
    
    return render_template("output.html",umrechnunskurse=currencyConversion , srcValue=srcValue, destOutput=str(output), srcCurrencyBlock=currencys[srcCurrency], destCurrencyBlock=currencys[destCurrency])

def loadDataFromCustoms(currency,monat,jahr): 
    max_day_in_month = calendar.monthrange(jahr,monat)[1]

    url = "http://www.zoll.de/SiteGlobals/Functions/Kurse/KursExport.xml?"\
    +"view=xmlexportkursesearchresultZOLLWeb&kursart=1&iso2code2="+currency\
    +"&startdatum_tag2=01&startdatum_monat2="+str(monat)+"&startdatum_jahr2="+str(jahr)\
    +"&enddatum_tag2="+str(max_day_in_month)+"&enddatum_monat2="+str(monat)+"&enddatum_jahr2="\
    +str(jahr)+"&sort=asc&spalte=gueltigkeit"

    r = requests.get(url)
    document = BeautifulSoup(r.content, "lxml")
    return float(document.find('kurswert').text.replace(",","."))

if __name__ == '__main__':
    app.run()
    
