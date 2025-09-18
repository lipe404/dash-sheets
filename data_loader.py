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

        # Abas disponíveis (você pode expandir esta lista conforme necessário)
        self.abas_disponiveis = [
            "Setembro", "Outubro", "Novembro", "Dezembro",
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio",
            "Junho", "Julho", "Agosto"
        ]

    def obter_gid_aba(self, sheet_id, nome_aba):
        """Tenta obter o GID da aba específica"""
        # GIDs comuns para diferentes abas (você pode expandir conforme necessário)
        gids_conhecidos = {
            "Setembro": ["0", "553357363", "135700763", "1208338902"],
            "Outubro": ["1", "553357364", "135700764", "1208338903"],
            "Novembro": ["2", "553357365", "135700765", "1208338904"],
            # Adicione mais conforme necessário
        }

        return gids_conhecidos.get(nome_aba, ["0"])

    def carregar_dados_vendedor(self, vendedor, sheet_id, aba_selecionada="Setembro"):
        """Carrega dados de um vendedor específico do Google Sheets de uma aba específica"""
        try:
            # Obtém possíveis GIDs para a aba
            gids_possiveis = self.obter_gid_aba(sheet_id, aba_selecionada)

            # Diferentes formatos de URL para tentar acessar a planilha
            urls_tentativas = []

            # Tenta com diferentes GIDs
            for gid in gids_possiveis:
                urls_tentativas.extend([
                    f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}",
                    f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}",
                ])

            # Tenta com nome da aba
            urls_tentativas.extend([
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_selecionada}",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&sheet={aba_selecionada}"
            ])

            df = pd.DataFrame()
            url_sucesso = None

            for url in urls_tentativas:
                try:
                    # Tenta carregar com requests primeiro
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        df = pd.read_csv(StringIO(response.text))
                        # Verifica se tem dados válidos
                        if not df.empty and len(df.columns) >= 3:
                            url_sucesso = url
                            break
                except:
                    try:
                        # Tenta com pandas diretamente
                        df = pd.read_csv(url)
                        if not df.empty and len(df.columns) >= 3:
                            url_sucesso = url
                            break
                    except:
                        continue

            if df.empty:
                st.warning(
                    f"Não foi possível acessar os dados de {vendedor} na aba '{aba_selecionada}'. Verifique se a planilha e aba estão públicas.")
                return pd.DataFrame()

            # Debug info (opcional - remova em produção)
            # st.info(f"Dados carregados de {vendedor} - Aba: {aba_selecionada} - URL: {url_sucesso}")

            # Limpa o DataFrame
            df = df.dropna(how='all')  # Remove linhas completamente vazias
            # Remove colunas completamente vazias
            df = df.dropna(axis=1, how='all')

            # Garante que temos pelo menos as colunas necessárias
            if len(df.columns) < 3:
                st.warning(
                    f"Planilha de {vendedor} (aba {aba_selecionada}) não tem colunas suficientes.")
                return pd.DataFrame()

            # Renomeia as colunas para padronizar (A, B, C, E = Data, Aluno, Telefone, Status)
            colunas_mapeamento = {}

            # Mapeia as colunas baseado na posição
            if len(df.columns) >= 1:
                colunas_mapeamento[0] = 'Data'
            if len(df.columns) >= 2:
                colunas_mapeamento[1] = 'Aluno'
            if len(df.columns) >= 3:
                colunas_mapeamento[2] = 'Telefone'

            # Para a coluna Status, tenta a posição 4 (coluna E), senão usa a última disponível
            if len(df.columns) >= 5:
                colunas_mapeamento[4] = 'Status'
            elif len(df.columns) >= 4:
                colunas_mapeamento[3] = 'Status'
            else:
                # Se não tem coluna suficiente, cria uma coluna Status padrão
                pass

            # Cria um novo DataFrame com as colunas corretas
            df_limpo = pd.DataFrame()
            for pos, nome_col in colunas_mapeamento.items():
                if pos < len(df.columns):
                    df_limpo[nome_col] = df.iloc[:, pos]

            # Se não conseguiu mapear a coluna Status, cria uma padrão
            if 'Status' not in df_limpo.columns:
                df_limpo['Status'] = 'SEM STATUS'

            # Remove linhas sem dados essenciais
            df_limpo = df_limpo.dropna(subset=['Data', 'Aluno'])

            # Adiciona coluna do vendedor e aba
            df_limpo['Vendedor'] = vendedor
            df_limpo['Aba'] = aba_selecionada

            return df_limpo

        except Exception as e:
            st.warning(
                f"Erro ao carregar dados do vendedor {vendedor} (aba {aba_selecionada}): {str(e)}")
            return pd.DataFrame()

    def carregar_todos_dados(self, aba_selecionada="Setembro"):
        """Carrega dados de todos os vendedores de uma aba específica"""
        dados_completos = []

        # Cria containers para progress
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        total_vendedores = len(self.vendedores_urls)
        vendedores_carregados = 0

        for i, (vendedor, sheet_id) in enumerate(self.vendedores_urls.items()):
            status_text.text(
                f'Carregando dados de {vendedor} (aba: {aba_selecionada})...')

            df_vendedor = self.carregar_dados_vendedor(
                vendedor, sheet_id, aba_selecionada)
            if not df_vendedor.empty:
                dados_completos.append(df_vendedor)
                vendedores_carregados += 1

            progress_bar.progress((i + 1) / total_vendedores)

        # Limpa os elementos de progresso
        progress_bar.empty()
        status_text.empty()

        if dados_completos:
            df_final = pd.concat(dados_completos, ignore_index=True)
            """st.success(
                f"✅ Dados carregados de {vendedores_carregados} vendedor(es) da aba '{aba_selecionada}'!")"""
            return df_final
        else:
            st.error(
                f"❌ Não foi possível carregar dados de nenhuma planilha da aba '{aba_selecionada}'.")
            return pd.DataFrame()

    def obter_abas_disponiveis(self):
        """Retorna lista de abas disponíveis"""
        return self.abas_disponiveis


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
            'Vendedor': random.choice(vendedores),
            'Aba': 'Setembro'  # Adiciona coluna Aba para dados demo
        })

    return pd.DataFrame(dados)
