import pandas as pd
from datetime import datetime, timedelta
import streamlit as st


def categorizar_status(status):
    """Categoriza os status em grupos principais"""
    if pd.isna(status):
        return "Perdido"

    status = str(status).upper().strip()

    # Status de leads fechados/convertidos
    status_fechados = ["PAGO"]

    # Status de leads em progresso
    status_progresso = [
        "EM NEGOCIAÇÃO", "AGUARDANDO INTERAÇÃO", "AGUARDANDO FICHA",
        "AGUARDANDO INTRA", "AGUARDANDO MENSAGEM",
        "AGUARDANDO O PREENCHIMENTO DA FICHA", "AGUARDANDO RETORNO",
        "AGUARDANDO PAGAMENTO"
    ]

    # Status de leads perdidos
    status_perdidos = [
        "NÃO RESPONDE", "SEM ENSINO MÉDIO", "NÃO POSSUÍ INTERESSE",
        "NÃO CONTÉ O CURSO QUE DESEJA", "NÃO TEM O CURSO",
        "ME BLOQUEOU", "OUTRO TIPO DE CURSO", "NÃO CONTÉM EXPERIENCIA",
        "NÃO POSSUI O CURSO QUE DESEJA", "GRADUAÇÃO"
    ]

    if any(s in status for s in status_fechados):
        return "Fechado"
    elif any(s in status for s in status_progresso):
        return "Em Progresso"
    elif any(s in status for s in status_perdidos):
        return "Perdido"
    else:
        return "Em Progresso"  # Default para status não categorizados


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
