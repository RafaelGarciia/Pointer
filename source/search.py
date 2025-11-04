import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta
from source.ui import utils
from math import floor


def search_worker(ticker: str, budget: utils.RealString):
    try:
        ticker = ticker.upper()   # Registra o ticker em maiusculo
        active = yf.Ticker(ticker)   # Instancia o ticker
        info = active.info or {}   # Arraw de info

        # Tenta obter o preço atual do ativo
        price = (
            info.get('currentPrice')
            or info.get('regularMarketPrice')
            or info.get('previousClose')
        )

        # Se não houver preço, retorna ValueError
        if price is None:
            raise ValueError(f'Preço do ativo "{ticker}" não disponivel.')

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

        # Iniciando as variaveis para o calculo
        budget_value: float = budget._get()   # Orçamento
        quotas = 0      # Cotas
        earnings = 0.0  # Proventos

        # Calcula as cotas com base no orçamento
        if price and price > 0 and budget_value > 0:
            # Quantas cotas consegue comprar com o valor de orçãmento
            quotas = floor(budget_value / price)
            # Quantos dividendos recebera com a quantidade de cotas compradas
            earnings = round(quotas * divs_year, 2)

            # Tag color categorize
            if divs_year > price * 0.15:
                tag = 'verde'   # Yield > 15% do preço
            elif divs_year > price * 0.10:
                tag = 'amarelo'   # Yield > 10% do preço
            elif divs_year > price * 0.01:
                tag = ''   # Yield > 5% do preço
            else:
                tag = ''

        # Compilação das informações em um dict
        data = {
            'ticker': ticker.rstrip('.SA'),
            'price': price,
            'divs_year': round(divs_year, 4),
            'quotas': quotas,
            'earnings': earnings,
            'tag': tag,
        }
        return ('ok', data)
    except Exception as exc:
        data = {
            'ticker': ticker.rstrip('.SA'),
            'price': '--',
            'divs_year': '--',
            'quotas': '--',
            'earnings': '--',
            'tag': '--',
        }
        return ('error', data)   # f'Erro buscando {ticker}: {exc}'
