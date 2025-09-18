import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from io import StringIO


class GoogleSheetsLoader:
    def __init__(self):
        self.vendedores_urls = {
            "Tayssa": "1DPdvJ-hWG-O9-F_iknNU7OP-Q9evSpsOfHS7FmqqZaM",
            "Maria Eduarda": "1xdAvHXE1aCbkQbAViHLSxI_BzKbS5J7byJ8bbBmMjnU",
            "Marya": "128BEya1w06bRtGC9J90vV0X7B7Yyp-pRaWgBr_3bxnk",
            "Danúbia": "1cIqwN5BL_synxO2gYH2QCqEG-0-GJUjTKLnSAs4-1M0",
            "Debóra": "1D50iY5pu7unzBO9we0xtk2_Ro9vIGH6T-kd8Z7v1DVA",
            "Felipe": "1hZLQ5-pQsKhRv4hSQZLS9k8KRSoYjzKAUmSnjKf9umg"
        }

    def carregar_dados_vendedor(self, vendedor, sheet_id):
        """Carrega dados de um vendedor específico do Google Sheets"""
        try:
            # URL para acessar a planilha como CSV
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Setembro"

            # Carrega os dados
            df = pd.read_csv(url)

            # Renomeia as colunas para padronizar
            colunas_esperadas = ['Data', 'Aluno',
                                 'Telefone', 'Coluna_D', 'Status']
            if len(df.columns) >= 5:
                df.columns = colunas_esperadas[:len(df.columns)]

            # Remove colunas desnecessárias se existirem
            colunas_necessarias = ['Data', 'Aluno', 'Telefone', 'Status']
            df = df[colunas_necessarias]

            # Adiciona coluna do vendedor
            df['Vendedor'] = vendedor

            return df

        except Exception as e:
            st.error(
                f"Erro ao carregar dados do vendedor {vendedor}: {str(e)}")
            return pd.DataFrame()

    def carregar_todos_dados(self):
        """Carrega dados de todos os vendedores"""
        dados_completos = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        total_vendedores = len(self.vendedores_urls)

        for i, (vendedor, sheet_id) in enumerate(self.vendedores_urls.items()):
            status_text.text(f'Carregando dados de {vendedor}...')

            df_vendedor = self.carregar_dados_vendedor(vendedor, sheet_id)
            if not df_vendedor.empty:
                dados_completos.append(df_vendedor)

            progress_bar.progress((i + 1) / total_vendedores)

        progress_bar.empty()
        status_text.empty()

        if dados_completos:
            df_final = pd.concat(dados_completos, ignore_index=True)
            return df_final
        else:
            return pd.DataFrame()

# Função alternativa para carregar dados (caso não tenha acesso às APIs do Google)


def carregar_dados_demo():
    """Carrega dados de demonstração para teste"""
    import random
    from datetime import datetime, timedelta

    vendedores = ["Tayssa", "Maria Eduarda",
                  "Marya", "Danúbia", "Debóra", "Felipe"]
    status_list = [
        "EM NEGOCIAÇÃO", "AGUARDANDO INTERAÇÃO", "NÃO RESPONDE",
        "AGUARDANDO FICHA", "SEM ENSINO MÉDIO", "GRADUAÇÃO", "PAGO",
        "NÃO POSSUÍ INTERESSE", "AGUARDANDO INTRA", "ME BLOQUEOU"
    ]

    dados = []

    for _ in range(500):  # 500 registros de exemplo
        data = datetime.now() - timedelta(days=random.randint(0, 90))
        dados.append({
            'Data': data.strftime('%Y-%m-%d'),
            'Aluno': f"Aluno {random.randint(1, 1000)}",
            'Telefone': f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            'Status': random.choice(status_list),
            'Vendedor': random.choice(vendedores)
        })

    return pd.DataFrame(dados)
