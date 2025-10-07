"""Verifica dados de risco."""

import MetaTrader5 as mt5
import json
import os
from datetime import date, datetime, time
from mtcli.logger import setup_logger
from .trades_model import calcular_lucro_total_dia
from mtcli_risco.mt5_context import mt5_conexao


log = setup_logger()


def carregar_estado(STATUS_FILE):
    """Carrega o estado do controle de risco."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            log.info(f"Carregando dados do arquivo {STATUS_FILE}")
            return json.load(f)
    return {"data": None, "bloqueado": False}


def salvar_estado(STATUS_FILE, data, bloqueado):
    """Salva o estado do controle de risco."""
    with open(STATUS_FILE, "w") as f:
        json.dump({"data": data.isoformat(), "bloqueado": bloqueado}, f)
        log.info(f"Salvando o estado: data {data} bloqueado {bloqueado}")


def encerrar_todas_posicoes():
    """Encerra todas as posições abertas."""
    with mt5_conexao():
        positions = mt5.positions_get()
    if not positions:
        log.info("Nenhuma posição aberta para fechar.")
        return

    with mt5_conexao():
        for pos in positions:
            tipo_oposto = (
                mt5.ORDER_TYPE_SELL
                if pos.type == mt5.ORDER_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            )
            ordem_fechar = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": tipo_oposto,
                "position": pos.ticket,
                "deviation": 10,
                "magic": 1000,
                "comment": "Fechando posição por limite de risco",
            }
            log.info(
                f"Requizição para encerramento de posições pelo risco: {ordem_fechar}"
            )
            resultado = mt5.order_send(ordem_fechar)

            if resultado is None:
                log.error("Erro ao enviar ordem: resultado é None.")
                continue

            if resultado.retcode != mt5.TRADE_RETCODE_DONE:
                log.error(f"Falha ao fechar posição {pos.ticket}: {resultado.retcode}")
            else:
                log.info(f"Posição {pos.ticket} fechada com sucesso.")


def cancelar_todas_ordens():
    """Cancela todas órdens pendentes."""
    with mt5_conexao():
        ordens = mt5.orders_get()
    if not ordens:
        log.info("Nenhuma ordem pendente para cancelar.")
        return

    with mt5_conexao():
        for ordem in ordens:
            resultado = mt5.order_delete(ordem.ticket)
            if resultado.retcode != mt5.TRADE_RETCODE_DONE:
                log.error(
                    f"Falha ao cancelar ordem {ordem.ticket}: {resultado.retcode}"
                )
            else:
                log.info(f"Ordem {ordem.ticket} cancelada com sucesso.")


def risco_excedido(limite):
    """Verifica se o loss limit do dia foi atingido."""
    try:
        total_lucro = calcular_lucro_total_dia()
        if total_lucro <= limite:
            log.info(
                f"Limite de prejuízo excedido! prejuízo: {total_lucro:.2f}, limite: {limite:.2f}"
            )
            return True
        return False
    except Exception as e:
        log.error(f"Erro ao verificar risco: {e}")
        return False
