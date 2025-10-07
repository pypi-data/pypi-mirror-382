# mtcli-rsi
  
Plugin do `mtcli` para calcular e exportar o indicador *RSI (Relative Strength Index)* a partir do MetaTrader 5 usando a linha de comando.
  
---
  
## Requisitos
  
- Python 3.10+
- MetaTrader 5 instalado e configurado
- Conta ativa em corretora compatível com MT5
  
---
  
## Instalação
  
Instale o plugin via pip:
  
```bash
pip install mtcli-rsi
```
  
---
  
## Uso
  
```bash
mt rsi --symbol WINN --period M5 --periodo 9 --bars 20
```
  
| Parâmetro        | Descrição                                              | Padrão  |
|------------|--------------------------------------|------|
| --symbol, -s | Símbolo do ativo                                       | WINN   |
| --period, -p | Timeframe dos candles (ex: M1, M5, H1, D1)             | M5      |
| --periodo, -pe | Período do RSI                                     | 9       |
| --bars         | Quantidade de candles                                 | 20      |
| --db           | Arquivo SQLite onde salvar os dados                   | rsi.db  |
  
---
  
Armazenamento
  
Os resultados do RSI são salvos em um arquivo SQLite com as colunas:
  
- RSI: valor do RSI (arredondado)
- close: preço de fechamento
- time: timestamp do candle
  
---
  
Exemplo de uso
  
```bash
mt rsi -s PETR4 -p M15 -pe 14 -bars 50 --db indicadores.db
```
  
---
  
## Contribuindo
  
Quer contribuir com o desenvolvimento, testes ou melhorias? Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md).
