import pandas as pd
from datetime import datetime, timedelta
import streamlit as st


def categorizar_status(status):
    """Categoriza os status em grupos principais"""
    if pd.isna(status):
        return "Perdido"

    status = str(status).strip()

    # Status de leads fechados/convertidos
    status_fechados = ["PAGO"]

    # Status de leads em progresso
    status_progresso = [
        "EM NEGOCIAÇÃO",
        "Aguardando retorno",
        "Aguardando pagamento",
        "AGUARDANDO INTERAÇÃO",
        "AGUARDANDO MENSAGEM",
        "AGUARDANDO INTRA",
        "EM PROCESSO"
    ]

    # Status de leads perdidos
    status_perdidos = [
        "NÃO POSSUÍ INTERESSE",
        "NÃO RESPONDE",
        "NÃO TEM O CURSO DE INTERESSE",
        "Não contém experiencia.",
        "Não tem o curso",
        "OUTRO TIPO DE CURSO",
        "NÃO POSSUI O TEMPO MINÍMO",
        "Não contém o curso desejado.",
        "não possui experiencia.",
        "PERDIDO"
    ]

    # Verifica correspondência exata primeiro
    if status in status_fechados:
        return "Fechado"
    elif status in status_progresso:
        return "Em Progresso"
    elif status in status_perdidos:
        return "Perdido"
    else:
        # Para status não categorizados, coloca como "Em Progresso" por padrão
        return "Em Progresso"


def formatar_numero(numero):
    """Formata números para exibição"""
    return f"{numero:,.0f}".replace(",", ".")


def formatar_percentual(valor):
    """Formata percentuais para exibição"""
    return f"{valor:.1f}%"


def validar_telefone(telefone):
    """Verifica se o telefone é válido (não vazio)"""
    if pd.isna(telefone):
        return False
    telefone_str = str(telefone).strip()
    return len(telefone_str) > 0 and telefone_str != "nan"


def validar_nome(nome):
    """Verifica se o nome é válido (não vazio)"""
    if pd.isna(nome):
        return False
    nome_str = str(nome).strip()
    return len(nome_str) > 0 and nome_str != "nan"


def obter_status_disponiveis():
    """Retorna lista de todos os status disponíveis organizados por categoria"""
    return {
        "Fechado": ["PAGO"],
        "Em Progresso": [
            "EM NEGOCIAÇÃO",
            "Aguardando retorno",
            "Aguardando pagamento",
            "AGUARDANDO INTERAÇÃO",
            "AGUARDANDO MENSAGEM",
            "AGUARDANDO INTRA",
            "EM PROCESSO"
        ],
        "Perdido": [
            "NÃO POSSUÍ INTERESSE",
            "NÃO RESPONDE",
            "NÃO TEM O CURSO DE INTERESSE",
            "Não contém experiencia.",
            "Não tem o curso",
            "OUTRO TIPO DE CURSO",
            "NÃO POSSUI O TEMPO MINÍMO",
            "Não contém o curso desejado.",
            "não possui experiencia.",
            "PERDIDO"
        ]
    }
