import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta
from math import floor
from time import sleep

def search_worker(ticker:str):
    try:
        ticker = ticker.upper() # Registra o ticker em maiusculo
        # Formata o ticker colocando .SA no final, para utilizar na busca
        ticker = ticker if ticker.upper().endswith('.SA') else f'{ticker.upper()}.SA'
        
        active = yf.Ticker(ticker) # Instancia o ticker
        info = active.info or {} # Arraw de info

        # Tenta obter o preço atual do ativo
        price = (
            info.get('currentPrice')
            or info.get('regularMarketPrice')
            or info.get('previousClose')
        )

        # Ultimos 12 meses de dividendos pagos pelo ativo
        start_date = (date.today() - relativedelta(years=1)).replace(day=1)
        divs = getattr(active, 'dividends', None)
        divs_year = 0.0

        # Filtra e soma os dividendos
        try:
            if divs is not None and not divs.empty:
                s = divs.loc[str(start_date) :]
                divs_year = float(s.tail(12).sum())
        except Exception:
            divs_year = 0.0

        # Compilação das informações em um dict
        data = {
            'ticker': ticker.rstrip('.SA'),
            'price': price,
            'divs_year': round(divs_year, 4),
        }
        return (True, data)
    except Exception as exc:
        data = {
            'ticker': ticker.rstrip('.SA'),
        }
        return (False, data)

