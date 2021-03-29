from flask import Flask, render_template, request

app = Flask(__name__)

currencyConversion = {
    "EUR-USD":1.1916,
    "USD-EUR":0.8392
    }

currencys = {
    "EUR": {
        "text":"Euro",
        "sign":"\u20ac"
        },
    "USD": {
        "text":"Dollar",
        "sign":"$"
        }        
    }


@app.route('/')
def start(): 
    srcValue = '1'
    srcCurrency = currencys['EUR']
    destCurrency = currencys['USD']
    
    return render_template("template.html", srcValue=srcValue, srcCurrencyBlock=srcCurrency, destCurrencyBlock=destCurrency)


@app.route('/calc')
def calcCurrency():
    srcValue = request.args.get("srcValue")
    srcCurrency = request.args.get("srcCurrency")
    destCurrency = request.args.get("destCurrency")
    key = srcCurrency + "-" + destCurrency
    rate = currencyConversion[key]
    
    value = float(srcValue.replace(",", "."))
    output = round(value * rate, 2)
    
    return render_template("output.html", srcValue=srcValue, destOutput=str(output), srcCurrencyBlock=currencys[srcCurrency], destCurrencyBlock=currencys[destCurrency])


if __name__ == '__main__':
    app.run()
    
