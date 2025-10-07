"""Lógica do RSI."""

import pandas as pd
from mtcli.logger import setup_logger

log = setup_logger()


def preparar_dataframe(rates):
    """Converte os dados de entrada em DataFrame e formata colunas iniciais."""
    df = pd.DataFrame(rates)
    df["close"] = df["close"].astype(float)
    return df


def calcular_rsi(df, periodo):
    """Calcula o RSI baseado no DataFrame de preços."""
    df["delta"] = df["close"].diff()
    gain = df["delta"].where(df["delta"] > 0, 0.0)
    loss = -df["delta"].where(df["delta"] < 0, 0.0)

    avg_gain = gain.rolling(window=periodo).mean()
    avg_loss = loss.rolling(window=periodo).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def formatar_resultado(df):
    """Arredonda RSI, formata timestamps e retorna apenas colunas relevantes."""
    df["RSI"] = df["RSI"].round(0)
    df_result = df[["RSI", "close", "time"]].dropna()
    df_result["time"] = pd.to_datetime(df_result["time"], unit="s")
    return df_result


def calcular_rsi_completo(rates, periodo):
    """Fluxo completo: prepara, calcula e formata o RSI."""
    df = preparar_dataframe(rates)
    df = calcular_rsi(df, periodo)
    return formatar_resultado(df)
