import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import re


def processar_data_inteligente(data_str):
    """Processa datas em diferentes formatos de forma inteligente"""
    if pd.isna(data_str):
        return None

    # Converte para string e limpa
    data_str = str(data_str).strip()

    # Remove aspas simples no final se existir
    if data_str.endswith("'"):
        data_str = data_str[:-1]

    # Se está vazio após limpeza
    if not data_str or data_str == 'nan':
        return None

    # Ano atual para completar datas incompletas
    ano_atual = datetime.now().year

    try:
        # Padrão 1: dd/mm/yyyy (completo)
        if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', data_str):
            return pd.to_datetime(data_str, format='%d/%m/%Y', errors='coerce')

        # Padrão 2: dd/mm/yy (ano com 2 dígitos)
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{2}$', data_str):
            return pd.to_datetime(data_str, format='%d/%m/%y', errors='coerce')

        # Padrão 3: dd/mm (sem ano - assume ano atual)
        elif re.match(r'^\d{1,2}/\d{1,2}$', data_str):
            data_str_completa = f"{data_str}/{ano_atual}"
            return pd.to_datetime(data_str_completa, format='%d/%m/%Y', errors='coerce')

        # Padrão 4: Tenta conversão automática do pandas
        else:
            return pd.to_datetime(data_str, errors='coerce')

    except Exception:
        return None


def categorizar_status(status):
    """Categoriza os status em grupos principais"""
    if pd.isna(status):
        return "Em Progresso"

    status = str(status).strip().upper()

    # Status de leads fechados/convertidos
    status_fechados = ["PAGO"]

    # Status de leads perdidos
    status_perdidos = [
        "LEAD PERDIDO",
        "NÃO RESPONDE"
    ]

    # Verifica correspondência exata primeiro
    if status in status_fechados:
        return "Fechado"
    elif status in status_perdidos:
        return "Perdido"
    elif status == "EM PROGRESSO":
        return "Em Progresso"
    else:
        # Para qualquer outro status, categoriza como "Em Progresso"
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
    return len(telefone_str) > 0 and telefone_str != "nan" and telefone_str != ""


def validar_nome(nome):
    """Verifica se o nome é válido (não vazio)"""
    if pd.isna(nome):
        return False
    nome_str = str(nome).strip()
    return len(nome_str) > 0 and nome_str != "nan" and nome_str != ""


def obter_status_disponiveis():
    """Retorna lista de todos os status disponíveis organizados por categoria"""
    return {
        "Fechado": ["PAGO"],
        "Em Progresso": ["EM PROGRESSO", "Outros status não especificados"],
        "Perdido": ["LEAD PERDIDO", "NÃO RESPONDE"]
    }


def limpar_dados_linha(linha):
    """Limpa uma linha de dados removendo valores inválidos"""
    linha_limpa = {}
    for coluna, valor in linha.items():
        if pd.isna(valor):
            linha_limpa[coluna] = ""
        else:
            valor_str = str(valor).strip()
            if valor_str.lower() in ['nan', 'none', 'null', '']:
                linha_limpa[coluna] = ""
            else:
                linha_limpa[coluna] = valor_str
    return linha_limpa
