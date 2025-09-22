import pandas as pd
import streamlit as st
import requests
from io import StringIO
import time
from utils import processar_data_inteligente, limpar_dados_linha


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

        # Abas disponíveis
        self.abas_disponiveis = [
            "Setembro", "Outubro", "Novembro", "Dezembro",
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio",
            "Junho", "Julho", "Agosto"
        ]

    def carregar_dados_vendedor(self, vendedor, sheet_id, aba_selecionada="Setembro"):
        """Carrega dados de um vendedor específico do Google Sheets de uma aba específica"""
        try:
            # Lista expandida de URLs para tentar acessar a planilha
            urls_tentativas = [
                # Formato 1: Export CSV com nome da aba
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&sheet={aba_selecionada}",
                # Formato 2: gviz com nome da aba
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_selecionada}",
                # Formato 3: Export CSV com GID 0 (primeira aba)
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
                # Formato 4: gviz com GID 0
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0",
                # Formato 5: Export CSV sem especificar aba (pega a primeira)
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
                # Formato 6: Tentativa com diferentes GIDs
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=2",
            ]

            df = pd.DataFrame()
            url_sucesso = None
            erro_detalhes = []

            for i, url in enumerate(urls_tentativas):
                try:
                    # Debug: mostra qual URL está sendo testada
                    if st.session_state.get('debug_mode', False):
                        st.write(
                            f"🔍 Testando URL {i+1} para {vendedor}: {url}")

                    # Tenta carregar com requests
                    response = requests.get(url, timeout=20)

                    if response.status_code == 200:
                        # Tenta decodificar o conteúdo
                        try:
                            content = response.content.decode('utf-8')
                        except UnicodeDecodeError:
                            content = response.content.decode('latin-1')

                        # Verifica se não é uma página de erro e tem conteúdo substancial
                        if ('error' not in content.lower() and
                            'not found' not in content.lower() and
                                len(content) > 50):

                            df = pd.read_csv(StringIO(content))

                            # Verifica se tem dados válidos (pelo menos 1 coluna)
                            if not df.empty and len(df.columns) >= 1:
                                url_sucesso = url
                                if st.session_state.get('debug_mode', False):
                                    st.success(
                                        f"✅ URL {i+1} funcionou! Shape: {df.shape}")
                                break

                    erro_detalhes.append(
                        f"URL {i+1}: Status {response.status_code}")

                except requests.exceptions.RequestException as e:
                    erro_detalhes.append(
                        f"URL {i+1}: Erro de conexão - {str(e)}")
                    continue
                except Exception as e:
                    erro_detalhes.append(f"URL {i+1}: Erro geral - {str(e)}")
                    continue

            if df.empty:
                st.warning(
                    f"⚠️ Não foi possível carregar dados de {vendedor} (aba: {aba_selecionada})")
                if st.session_state.get('debug_mode', False):
                    st.write("Detalhes dos erros:", erro_detalhes)
                return pd.DataFrame()

            # Debug: mostra informações sobre os dados carregados
            if st.session_state.get('debug_mode', False):
                st.success(
                    f"✅ Dados carregados de {vendedor} via: {url_sucesso}")
                st.write(f"Shape original: {df.shape}")
                st.write("Primeiras 3 colunas:", list(df.columns[:3]))

            # Processa o DataFrame
            df_processado = self.processar_dataframe_inteligente(
                df, vendedor, aba_selecionada)

            return df_processado

        except Exception as e:
            st.error(f"❌ Erro crítico ao carregar {vendedor}: {str(e)}")
            return pd.DataFrame()

    def processar_dataframe_inteligente(self, df, vendedor, aba_selecionada):
        """Processa e limpa o DataFrame carregado de forma inteligente"""
        try:
            # Debug: mostra o DataFrame original
            if st.session_state.get('debug_mode', False):
                st.write(f"📊 DataFrame original de {vendedor}:")
                st.write(f"Shape: {df.shape}")
                st.write("Primeiras 3 linhas:")
                st.dataframe(df.head(3))

            # Remove colunas completamente vazias
            df = df.dropna(axis=1, how='all')

            if df.empty or len(df.columns) < 3:
                if st.session_state.get('debug_mode', False):
                    st.warning(
                        f"⚠️ {vendedor}: DataFrame vazio ou com poucas colunas após limpeza")
                return pd.DataFrame()

            # Detecta e remove linhas de cabeçalho
            df = self.detectar_e_remover_cabecalhos(df)

            # Garante que temos pelo menos 3 colunas (Data, Aluno, Telefone)
            if len(df.columns) < 3:
                if st.session_state.get('debug_mode', False):
                    st.warning(
                        f"⚠️ {vendedor}: Menos de 3 colunas disponíveis")
                return pd.DataFrame()

            # Mapeia as colunas de forma inteligente
            df_limpo = self.mapear_colunas_inteligente(df)

            # Processa as datas de forma inteligente
            df_limpo['Data_Original'] = df_limpo['Data'].copy()
            df_limpo['Data'] = df_limpo['Data'].apply(
                processar_data_inteligente)

            # Remove apenas linhas onde TANTO data quanto aluno/telefone estão vazios
            # (permite leads só com telefone ou só com nome)
            condicoes_validas = (
                (df_limpo['Data'].notna()) &  # Data deve ser válida
                (
                    # Nome OU
                    (df_limpo['Aluno'].astype(str).str.strip() != '') |
                    (df_limpo['Telefone'].astype(
                        str).str.strip() != '')  # Telefone
                )
            )

            df_limpo = df_limpo[condicoes_validas]

            # Adiciona informações do vendedor e aba
            df_limpo['Vendedor'] = vendedor
            df_limpo['Aba'] = aba_selecionada

            # Debug: mostra o resultado final
            if st.session_state.get('debug_mode', False):
                st.write(f"📈 DataFrame processado de {vendedor}:")
                st.write(f"Registros válidos: {len(df_limpo)}")
                if len(df_limpo) > 0:
                    st.write("Amostra dos dados processados:")
                    st.dataframe(df_limpo.head(3))

            return df_limpo

        except Exception as e:
            st.error(f"❌ Erro ao processar dados de {vendedor}: {str(e)}")
            if st.session_state.get('debug_mode', False):
                st.write(f"Erro detalhado: {type(e).__name__}: {str(e)}")
            return pd.DataFrame()

    def detectar_e_remover_cabecalhos(self, df):
        """Detecta e remove linhas de cabeçalho automaticamente"""
        if df.empty:
            return df

        # Palavras-chave que indicam cabeçalhos
        palavras_cabecalho = [
            'data', 'nome', 'aluno', 'telefone', 'status', 'lead',
            'cliente', 'contato', 'whatsapp', 'celular', 'situacao'
        ]

        linhas_para_remover = []

        # Verifica as primeiras 5 linhas
        for i in range(min(5, len(df))):
            linha_str = ' '.join(df.iloc[i].astype(str)).lower()

            # Se encontrar 2 ou mais palavras-chave, considera cabeçalho
            palavras_encontradas = sum(
                1 for palavra in palavras_cabecalho if palavra in linha_str)
            if palavras_encontradas >= 2:
                linhas_para_remover.append(i)

        # Remove as linhas identificadas como cabeçalho
        if linhas_para_remover:
            df = df.drop(df.index[linhas_para_remover]).reset_index(drop=True)

        return df

    def mapear_colunas_inteligente(self, df):
        """Mapeia as colunas de forma inteligente baseado no conteúdo"""
        df_limpo = pd.DataFrame()

        # Mapeia as colunas baseado na posição (padrão)
        # Coluna A (índice 0) = Data
        df_limpo['Data'] = df.iloc[:, 0] if len(df.columns) > 0 else ""

        # Coluna B (índice 1) = Aluno
        df_limpo['Aluno'] = df.iloc[:, 1] if len(df.columns) > 1 else ""

        # Coluna C (índice 2) = Telefone
        df_limpo['Telefone'] = df.iloc[:, 2] if len(df.columns) > 2 else ""

        # Coluna E (índice 4) = Status, com fallbacks
        if len(df.columns) >= 5:
            df_limpo['Status'] = df.iloc[:, 4]  # Coluna E
        elif len(df.columns) >= 4:
            df_limpo['Status'] = df.iloc[:, 3]  # Coluna D
        else:
            df_limpo['Status'] = 'EM PROGRESSO'  # Padrão

        return df_limpo

    def carregar_todos_dados(self, aba_selecionada="Setembro"):
        """Carrega dados de todos os vendedores de uma aba específica"""
        dados_completos = []

        # Cria barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_vendedores = len(self.vendedores_urls)
        vendedores_carregados = 0
        total_registros = 0

        for i, (vendedor, sheet_id) in enumerate(self.vendedores_urls.items()):
            status_text.text(
                f'🔄 Carregando dados de {vendedor} (aba: {aba_selecionada})...')

            df_vendedor = self.carregar_dados_vendedor(
                vendedor, sheet_id, aba_selecionada)

            if not df_vendedor.empty:
                dados_completos.append(df_vendedor)
                vendedores_carregados += 1
                total_registros += len(df_vendedor)
                status_text.text(
                    f'✅ {vendedor}: {len(df_vendedor)} registros carregados')
            else:
                status_text.text(f'❌ {vendedor}: Nenhum dado carregado')

            progress_bar.progress((i + 1) / total_vendedores)
            time.sleep(0.3)  # Pausa menor para ser mais rápido

        # Limpa os elementos de progresso
        progress_bar.empty()
        status_text.empty()

        if dados_completos:
            df_final = pd.concat(dados_completos, ignore_index=True)
            st.success(
                f"✅ Dados carregados de {vendedores_carregados}/{total_vendedores} vendedores!")
            st.info(f"📊 Total de registros carregados: {len(df_final)}")

            # Mostra estatísticas por vendedor
            if st.session_state.get('debug_mode', False):
                st.write("📈 Registros por vendedor:")
                stats_vendedor = df_final.groupby(
                    'Vendedor').size().sort_values(ascending=False)
                st.write(stats_vendedor)

            return df_final
        else:
            st.error(
                f"❌ Não foi possível carregar dados de nenhuma planilha da aba '{aba_selecionada}'.")
            st.info("💡 Verifique se as planilhas estão públicas e se a aba existe.")
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

    # Status atualizados conforme especificação
    status_list = [
        "LEAD PERDIDO",
        "EM PROGRESSO",
        "PAGO",
        "NÃO RESPONDE",
        "AGUARDANDO RETORNO",
        "NEGOCIANDO",
        "INTERESSADO"
    ]

    dados = []

    # Gera dados de demonstração mais realistas
    for _ in range(800):  # Mais dados para simular planilhas reais
        data = datetime.now() - timedelta(days=random.randint(0, 120))

        # Simula diferentes formatos de data
        formato_data = random.choice([
            data.strftime('%d/%m/%Y'),
            data.strftime('%d/%m/%y'),
            data.strftime('%d/%m'),
        ])

        # Alguns leads só com telefone, outros só com nome
        if random.random() > 0.3:  # 70% têm nome
            nome_aluno = f"Aluno {random.randint(1000, 9999)}"
        else:
            nome_aluno = ""

        if random.random() > 0.2:  # 80% têm telefone
            telefone = f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        else:
            telefone = ""

        # Garante que pelo menos um dos dois (nome ou telefone) existe
        if not nome_aluno and not telefone:
            if random.random() > 0.5:
                nome_aluno = f"Aluno {random.randint(1000, 9999)}"
            else:
                telefone = f"({random.randint(11, 99)}) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

        dados.append({
            'Data': formato_data,
            'Aluno': nome_aluno,
            'Telefone': telefone,
            'Status': random.choice(status_list),
            'Vendedor': random.choice(vendedores),
            'Aba': 'Setembro'
        })

    return pd.DataFrame(dados)
