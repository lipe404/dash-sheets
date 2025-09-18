import pandas as pd
import streamlit as st
import requests
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
            # Diferentes formatos de URL para tentar acessar a planilha
            urls_tentativas = [
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Setembro",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&sheet=Setembro"
            ]

            df = pd.DataFrame()

            for url in urls_tentativas:
                try:
                    # Tenta carregar com requests primeiro
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        df = pd.read_csv(StringIO(response.text))
                        break
                    else:
                        # Tenta com pandas diretamente
                        df = pd.read_csv(url)
                        break
                except:
                    continue

            if df.empty:
                st.warning(
                    f"Não foi possível acessar os dados de {vendedor}. Verifique se a planilha está pública.")
                return pd.DataFrame()

            # Limpa o DataFrame
            df = df.dropna(how='all')  # Remove linhas completamente vazias
            # Remove colunas completamente vazias
            df = df.dropna(axis=1, how='all')

            # Garante que temos pelo menos as colunas necessárias
            if len(df.columns) < 4:
                st.warning(
                    f"Planilha de {vendedor} não tem colunas suficientes.")
                return pd.DataFrame()

            # Renomeia as colunas para padronizar (A, B, C, E = Data, Aluno, Telefone, Status)
            colunas_mapeamento = {
                0: 'Data',
                1: 'Aluno',
                2: 'Telefone',
                # Coluna E ou D se não houver E
                4: 'Status' if len(df.columns) > 4 else 3
            }

            # Cria um novo DataFrame com as colunas corretas
            df_limpo = pd.DataFrame()
            for pos, nome_col in colunas_mapeamento.items():
                if pos < len(df.columns):
                    df_limpo[nome_col] = df.iloc[:, pos]
                else:
                    df_limpo[nome_col] = None

            # Se não temos coluna Status na posição correta, usa a última coluna disponível
            if 'Status' not in df_limpo.columns or df_limpo['Status'].isna().all():
                if len(df.columns) >= 4:
                    df_limpo['Status'] = df.iloc[:, -1]  # Última coluna
                else:
                    df_limpo['Status'] = 'SEM STATUS'

            # Remove linhas sem dados essenciais
            df_limpo = df_limpo.dropna(subset=['Data', 'Aluno'])

            # Adiciona coluna do vendedor
            df_limpo['Vendedor'] = vendedor

            return df_limpo

        except Exception as e:
            st.warning(
                f"Erro ao carregar dados do vendedor {vendedor}: {str(e)}")
            return pd.DataFrame()

    def carregar_todos_dados(self):
        """Carrega dados de todos os vendedores"""
        dados_completos = []

        # Cria containers para progress
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        total_vendedores = len(self.vendedores_urls)
        vendedores_carregados = 0

        for i, (vendedor, sheet_id) in enumerate(self.vendedores_urls.items()):
            status_text.text(f'Carregando dados de {vendedor}...')

            df_vendedor = self.carregar_dados_vendedor(vendedor, sheet_id)
            if not df_vendedor.empty:
                dados_completos.append(df_vendedor)
                vendedores_carregados += 1

            progress_bar.progress((i + 1) / total_vendedores)

        # Limpa os elementos de progresso
        progress_bar.empty()
        status_text.empty()

        if dados_completos:
            df_final = pd.concat(dados_completos, ignore_index=True)
            # st.success(
            # f"✅ Dados carregados com sucesso de {vendedores_carregados} vendedor(es)!")
            return df_final
        else:
            st.error("❌ Não foi possível carregar dados de nenhuma planilha.")
            return pd.DataFrame()


def carregar_dados_demo():
    """Carrega dados de demonstração para teste"""
    import random
    from datetime import datetime, timedelta

    vendedores = ["Tayssa", "Maria Eduarda",
                  "Marya", "Danúbia", "Debóra", "Felipe"]
    status_list = [
        "EM NEGOCIAÇÃO", "AGUARDANDO INTERAÇÃO", "NÃO RESPONDE",
        "AGUARDANDO FICHA", "SEM ENSINO MÉDIO", "GRADUAÇÃO", "PAGO",
        "NÃO POSSUÍ INTERESSE", "AGUARDANDO INTRA", "ME BLOQUEOU",
        "OUTRO TIPO DE CURSO", "AGUARDANDO RETORNO", "AGUARDANDO PAGAMENTO"
    ]

    dados = []

    # Gera dados mais realistas
    for _ in range(500):
        data = datetime.now() - timedelta(days=random.randint(0, 90))
        nome_aluno = f"Aluno {random.randint(1000, 9999)}"

        # Alguns leads sem telefone (mais realista)
        if random.random() > 0.1:  # 90% têm telefone
            telefone = f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        else:
            telefone = ""

        dados.append({
            'Data': data.strftime('%d/%m/%Y'),
            'Aluno': nome_aluno,
            'Telefone': telefone,
            'Status': random.choice(status_list),
            'Vendedor': random.choice(vendedores)
        })

    return pd.DataFrame(dados)
