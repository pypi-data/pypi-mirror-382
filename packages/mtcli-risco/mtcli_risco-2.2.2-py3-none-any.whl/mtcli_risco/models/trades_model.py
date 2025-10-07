"""Cálculos do lucro do dia."""

import MetaTrader5 as mt5
from datetime import date, datetime, time
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from mtcli_risco.mt5_context import mt5_conexao


log = setup_logger()


def contar_transacoes_realizadas() -> int:
    """Conta a quantidade de posições encerradas no dia (transações de fechamento)."""
    hoje = datetime.now().date()
    inicio = datetime.combine(hoje, time(0, 0))
    fim = datetime.combine(hoje, time(23, 59))

    with mt5_conexao():
        deals = mt5.history_deals_get(inicio, fim)

    if deals is None:
        log.warning("Nenhum deal retornado.")
        return 0

    if not isinstance(deals, (list, tuple)):
        deals = [deals]

    # Types 1 = buy, 2 = sell → usados para fechar posições
    transacoes = [d for d in deals if d.type in (1, 2)]

    log.info(f"Transações realizadas hoje: {len(transacoes)}")
    return len(transacoes)


def calcular_lucro_realizado() -> float:
    """Calcula o lucro realizado do dia."""
    hoje = datetime.now().date()
    inicio = datetime.combine(hoje, time(0, 0))
    fim = datetime.combine(hoje, time(23, 59))

    with mt5_conexao():
        deals = mt5.history_deals_get(inicio, fim)
        log.info(f"Deals recebidos: {len(deals) if deals else 0}")

    if deals is None or len(deals) == 0:
        log.warning("Nenhum deal retornado.")
        return 0.0

    lucro_realizado = sum(
        deal.profit for deal in deals if deal.entry == mt5.DEAL_ENTRY_OUT
    )

    log.info(f"Lucro realizado do dia: {lucro_realizado:.2f}")
    return lucro_realizado


def obter_lucro_aberto() -> float:
    """Obtem o lucro em aberto."""
    with mt5_conexao():
        info = mt5.account_info()

    lucro_aberto = info.profit if info else 0.0
    log.info(f"lucro aberto: {lucro_aberto:.2f}")

    return lucro_aberto


def calcular_lucro_total_dia() -> float:
    """Calcula o lucro total do dia."""
    realizado = calcular_lucro_realizado()
    aberto = obter_lucro_aberto()
    total = realizado + aberto
    log.info(
        f"Lucro realizado: {realizado:.2f}, lucro aberto: {aberto:.2f}, total: {total:.2f}"
    )
    return total
