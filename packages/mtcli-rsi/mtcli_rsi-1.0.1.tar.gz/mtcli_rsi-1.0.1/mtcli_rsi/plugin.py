"""Comando RSI."""

import click
import MetaTrader5 as mt5
import pandas as pd
import sqlite3
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from .rsi import calcular_rsi_completo


log = setup_logger()


@click.command("rsi", help="Calcula o indicador RSI (Índice de Força Relativa) para o ativo informado.")
@click.version_option(package_name="mtcli-rsi")
@click.option(
    "--symbol", "-s", default="WIN$N", help="Símbolo do ativo (default WIN$N)."
)
@click.option("--period", "-p", default="M5", help="Timeframe (default M5)")
@click.option("--periodo", "-pe", default=9, help="Período do RSI (default 9).")
@click.option(
    "--bars", type=int, default=20, help="Número de candles para análise (default 20)."
)
@click.option("--db", default="rsi.db", help="Arquivo SQLite (default rsi.db).")
def rsi(symbol, period, periodo, bars, db):
    """Calcula o RSI do ativo symbol."""
    conectar()

    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M2": mt5.TIMEFRAME_M2,
        "M3": mt5.TIMEFRAME_M3,
        "M4": mt5.TIMEFRAME_M4,
        "M5": mt5.TIMEFRAME_M5,
        "M6": mt5.TIMEFRAME_M6,
        "M10": mt5.TIMEFRAME_M10,
        "M12": mt5.TIMEFRAME_M12,
        "M15": mt5.TIMEFRAME_M15,
        "M20": mt5.TIMEFRAME_M20,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H2": mt5.TIMEFRAME_H2,
        "H3": mt5.TIMEFRAME_H3,
        "H4": mt5.TIMEFRAME_H4,
        "H6": mt5.TIMEFRAME_H6,
        "H8": mt5.TIMEFRAME_H8,
        "H12": mt5.TIMEFRAME_H12,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1,
    }

    if period.upper() not in tf_map:
        click.echo(f"Timeframe {period} inválido")
        log.error(f"Timeframe {period} inválido")
        return

    rates = mt5.copy_rates_from_pos(symbol, tf_map[period], 0, bars + periodo)
    shutdown()

    if rates is None or len(rates) == 0:
        click.echo(f"Erro ao obter dados do {symbol}.")
        log.error(f"Erro ao obter dados do {symbol}.")
        return

    df_result = calcular_rsi_completo(rates, periodo)
    click.echo(df_result.tail(5).to_string(index=False))

    conn = sqlite3.connect(db)
    df_result.to_sql("rsi", conn, if_exists="append", index=False)
    conn.close()

    log.info(
        f"Dados RSI salvos em {db} (tabela rsi) - símbolo: {symbol}, timeframe: {period}, período: {periodo}"
    )


if __name__ == "__main__":
    rsi()
