import pandas as pd
from datetime import datetime
from utils import categorizar_status, validar_telefone, validar_nome


class DataProcessor:
    def __init__(self, df):
        self.df = df.copy()
        self.processar_dados()

    def processar_dados(self):
        """Processa e limpa os dados"""
        if self.df.empty:
            return

        # Converte a coluna de data
        self.df['Data'] = pd.to_datetime(self.df['Data'], errors='coerce')

        # Remove registros sem data válida
        self.df = self.df.dropna(subset=['Data'])

        # Categoriza os status
        self.df['Status_Categoria'] = self.df['Status'].apply(
            categorizar_status)

        # Valida telefones e nomes
        self.df['Tem_Telefone'] = self.df['Telefone'].apply(validar_telefone)
        self.df['Tem_Nome'] = self.df['Aluno'].apply(validar_nome)

        # Adiciona coluna de mês/ano para agrupamentos
        self.df['Mes_Ano'] = self.df['Data'].dt.to_period('M')
        self.df['Data_Formatada'] = self.df['Data'].dt.strftime('%d/%m/%Y')

    def filtrar_dados(self, vendedores_selecionados, data_inicio, data_fim):
        """Filtra os dados baseado nos critérios selecionados"""
        df_filtrado = self.df.copy()

        # Filtro por vendedor
        if vendedores_selecionados:
            df_filtrado = df_filtrado[df_filtrado['Vendedor'].isin(
                vendedores_selecionados)]

        # Filtro por data
        if data_inicio and data_fim:
            df_filtrado = df_filtrado[
                (df_filtrado['Data'] >= pd.to_datetime(data_inicio)) &
                (df_filtrado['Data'] <= pd.to_datetime(data_fim))
            ]

        return df_filtrado

    def calcular_kpis(self, df_filtrado):
        """Calcula os KPIs principais"""
        if df_filtrado.empty:
            return {
                'total_leads': 0,
                'leads_com_nome': 0,
                'leads_com_telefone': 0,
                'leads_com_status': 0,
                'vendas_fechadas': 0,
                'leads_perdidos': 0,
                'taxa_conversao': 0,
                'funil_total': 0,
                'funil_convertidos': 0,
                'funil_progresso': 0,
                'funil_perdidos': 0
            }

        total_leads = len(df_filtrado)
        leads_com_nome = df_filtrado['Tem_Nome'].sum()
        leads_com_telefone = df_filtrado['Tem_Telefone'].sum()
        leads_com_status = df_filtrado['Status'].notna().sum()

        vendas_fechadas = len(
            df_filtrado[df_filtrado['Status_Categoria'] == 'Fechado'])
        leads_perdidos = len(
            df_filtrado[df_filtrado['Status_Categoria'] == 'Perdido'])
        leads_progresso = len(
            df_filtrado[df_filtrado['Status_Categoria'] == 'Em Progresso'])

        taxa_conversao = (vendas_fechadas / total_leads *
                          100) if total_leads > 0 else 0

        return {
            'total_leads': total_leads,
            'leads_com_nome': leads_com_nome,
            'leads_com_telefone': leads_com_telefone,
            'leads_com_status': leads_com_status,
            'vendas_fechadas': vendas_fechadas,
            'leads_perdidos': leads_perdidos,
            'taxa_conversao': taxa_conversao,
            'funil_total': total_leads,
            'funil_convertidos': vendas_fechadas,
            'funil_progresso': leads_progresso,
            'funil_perdidos': leads_perdidos
        }

    def obter_dados_por_vendedor(self, df_filtrado):
        """Calcula métricas por vendedor"""
        if df_filtrado.empty:
            return pd.DataFrame()

        vendedor_stats = df_filtrado.groupby('Vendedor').agg({
            'Aluno': 'count',
            'Status_Categoria': lambda x: (x == 'Fechado').sum()
        }).reset_index()

        vendedor_stats.columns = ['Vendedor', 'Total_Leads', 'Vendas_Fechadas']
        vendedor_stats['Leads_Perdidos'] = df_filtrado.groupby('Vendedor')['Status_Categoria'].apply(
            lambda x: (x == 'Perdido').sum()
        ).values

        vendedor_stats['Taxa_Conversao'] = (
            vendedor_stats['Vendas_Fechadas'] /
            vendedor_stats['Total_Leads'] * 100
        ).fillna(0)

        return vendedor_stats

    def obter_leads_por_tempo(self, df_filtrado):
        """Obtém dados de leads criados ao longo do tempo"""
        if df_filtrado.empty:
            return pd.DataFrame()

        leads_tempo = df_filtrado.groupby(
            'Data').size().reset_index(name='Quantidade')
        leads_tempo = leads_tempo.sort_values('Data')

        return leads_tempo
