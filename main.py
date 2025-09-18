import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Importa os módulos personalizados
from data_loader import GoogleSheetsLoader, carregar_dados_demo
from data_processor import DataProcessor
from visualizations import DashboardCharts
from utils import formatar_numero, formatar_percentual

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - Sheets",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric > label {
        font-size: 14px !important;
    }
    .stMetric > div {
        font-size: 24px !important;
    }
    .stAlert > div {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def carregar_dados():
    """Carrega os dados com cache"""
    try:
        loader = GoogleSheetsLoader()
        df = loader.carregar_todos_dados()
        if df.empty:
            st.warning(
                "Não foi possível carregar dados do Google Sheets. Usando dados de demonstração.")
            df = carregar_dados_demo()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.info("Carregando dados de demonstração...")
        return carregar_dados_demo()


def main():
    # Título principal
    st.title("📊 Dashboard de Vendas - Sheets")
    st.markdown("---")

    # Carrega os dados
    with st.spinner("Carregando dados..."):
        df_raw = carregar_dados()

    if df_raw.empty:
        st.error("Não foi possível carregar os dados.")
        st.info(
            "Verifique se as planilhas do Google Sheets estão públicas e acessíveis.")
        return

    # Processa os dados
    processor = DataProcessor(df_raw)
    charts = DashboardCharts()

    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")

    # Filtro de vendedor
    vendedores_disponiveis = sorted(df_raw['Vendedor'].unique())
    vendedores_selecionados = st.sidebar.multiselect(
        "Selecione os Vendedores:",
        options=vendedores_disponiveis,
        default=vendedores_disponiveis
    )

    # Filtro de período
    st.sidebar.subheader("📅 Período")

    # Data mínima e máxima dos dados
    try:
        data_min = pd.to_datetime(df_raw['Data'], errors='coerce').min().date()
        data_max = pd.to_datetime(df_raw['Data'], errors='coerce').max().date()
    except:
        data_min = datetime.now().date() - timedelta(days=90)
        data_max = datetime.now().date()

    col1, col2 = st.sidebar.columns(2)
    with col1:
        data_inicio = st.date_input(
            "Data Início:",
            value=data_min,
            min_value=data_min,
            max_value=data_max
        )

    with col2:
        data_fim = st.date_input(
            "Data Fim:",
            value=data_max,
            min_value=data_min,
            max_value=data_max
        )

    # Botão para atualizar dados
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()

    # Informações sobre os dados carregados
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Informações")
    st.sidebar.info(f"Total de registros: {len(df_raw)}")
    st.sidebar.info(f"Vendedores: {len(vendedores_disponiveis)}")

    # Aplica filtros
    df_filtrado = processor.filtrar_dados(
        vendedores_selecionados, data_inicio, data_fim)

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        return

    # Calcula KPIs
    kpis = processor.calcular_kpis(df_filtrado)
    df_vendedor = processor.obter_dados_por_vendedor(df_filtrado)
    df_tempo = processor.obter_leads_por_tempo(df_filtrado)

    # Seção de KPIs principais
    st.header("📈 KPIs Principais")

    # KPIs sempre visíveis (resumo)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="👥 Total de Leads",
            value=formatar_numero(kpis['total_leads'])
        )

    with col2:
        st.metric(
            label="✅ Vendas Fechadas",
            value=formatar_numero(kpis['vendas_fechadas'])
        )

    with col3:
        st.metric(
            label="📊 Taxa de Conversão",
            value=formatar_percentual(kpis['taxa_conversao'])
        )

    with col4:
        st.metric(
            label="❌ Leads Perdidos",
            value=formatar_numero(kpis['leads_perdidos'])
        )

    # Expander para KPIs adicionais
    with st.expander("📋 Ver KPIs Detalhados Adicionais", expanded=False):
        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.metric(
                label="📝 Leads com Nome",
                value=formatar_numero(kpis['leads_com_nome'])
            )

        with col6:
            st.metric(
                label="📞 Leads com Telefone",
                value=formatar_numero(kpis['leads_com_telefone'])
            )

        with col7:
            st.metric(
                label="🏷️ Leads com Status",
                value=formatar_numero(kpis['leads_com_status'])
            )

        with col8:
            st.metric(
                label="⏳ Em Progresso",
                value=formatar_numero(kpis['funil_progresso'])
            )

    st.markdown("---")

    # Gráficos principais
    col1, col2 = st.columns(2)

    with col1:
        # Funil de vendas
        fig_funil = charts.criar_funil_vendas(kpis)
        st.plotly_chart(fig_funil, use_container_width=True)

        # KPIs do funil
        st.subheader("📊 Métricas do Funil")
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

        with kpi_col1:
            st.metric("Total no Funil", formatar_numero(kpis['funil_total']))
        with kpi_col2:
            st.metric("Convertidos", formatar_numero(
                kpis['funil_convertidos']))
        with kpi_col3:
            st.metric("Em Progresso", formatar_numero(kpis['funil_progresso']))
        with kpi_col4:
            st.metric("Perdidos", formatar_numero(kpis['funil_perdidos']))

    with col2:
        # Taxa de conversão por vendedor
        fig_conversao = charts.criar_conversao_vendedor(df_vendedor)
        st.plotly_chart(fig_conversao, use_container_width=True)

    # Segunda linha de gráficos
    col3, col4 = st.columns(2)

    with col3:
        # Pizza de distribuição por status
        fig_pizza = charts.criar_pizza_status(df_filtrado)
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col4:
        # Performance por vendedor
        fig_performance = charts.criar_performance_vendedor(df_vendedor)
        st.plotly_chart(fig_performance, use_container_width=True)

    # Gráfico de leads ao longo do tempo
    st.subheader("📈 Leads Criados ao Longo do Tempo")
    fig_tempo = charts.criar_leads_tempo(df_tempo)
    st.plotly_chart(fig_tempo, use_container_width=True)

    # Tabela de dados detalhados
    st.markdown("---")
    st.header("📋 Dados Detalhados")

    # Opções de visualização da tabela
    col1, col2, col3 = st.columns(3)

    with col1:
        colunas_disponiveis = ['Data_Formatada', 'Vendedor',
                               'Aluno', 'Telefone', 'Status', 'Status_Categoria']
        mostrar_colunas = st.multiselect(
            "Selecione as colunas:",
            options=colunas_disponiveis,
            default=['Data_Formatada', 'Vendedor', 'Aluno', 'Status']
        )

    with col2:
        linhas_por_pagina = st.selectbox(
            "Linhas por página:",
            options=[10, 25, 50, 100],
            index=1
        )

    with col3:
        # Opções de ordenação baseadas nas colunas disponíveis no DataFrame filtrado
        colunas_ordenacao = ['Data_Formatada', 'Vendedor', 'Aluno', 'Status']
        ordenar_por = st.selectbox(
            "Ordenar por:",
            options=colunas_ordenacao,
            index=0
        )

    # Exibe a tabela
    if mostrar_colunas:
        try:
            df_exibicao = df_filtrado[mostrar_colunas].copy()

            # Ordena os dados - verifica se a coluna existe
            if ordenar_por in df_exibicao.columns:
                df_exibicao = df_exibicao.sort_values(
                    ordenar_por, ascending=False)
            else:
                st.warning(
                    f"Coluna '{ordenar_por}' não encontrada para ordenação.")

            # Paginação
            total_linhas = len(df_exibicao)
            total_paginas = max(1, (total_linhas - 1) // linhas_por_pagina + 1)

            if total_paginas > 1:
                pagina = st.number_input(
                    f"Página (1 a {total_paginas}):",
                    min_value=1,
                    max_value=total_paginas,
                    value=1
                )

                inicio = (pagina - 1) * linhas_por_pagina
                fim = inicio + linhas_por_pagina
                df_exibicao = df_exibicao.iloc[inicio:fim]

            st.dataframe(df_exibicao, use_container_width=True)

            # Informações da tabela
            st.info(
                f"Mostrando {len(df_exibicao)} de {total_linhas} registros")

        except Exception as e:
            st.error(f"Erro ao exibir tabela: {str(e)}")

    # Botão para download dos dados
    if st.button("📥 Download dos Dados (CSV)"):
        try:
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name=f"dados_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Erro ao gerar CSV: {str(e)}")


if __name__ == "__main__":
    main()
