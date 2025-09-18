import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class DashboardCharts:
    def __init__(self):
        self.cores = {
            'Em Progresso': '#3498db',  # Azul
            'Fechado': '#2ecc71',       # Verde
            'Perdido': '#e74c3c'        # Vermelho
        }

    def criar_funil_vendas(self, kpis):
        """Cria o gráfico de funil de vendas"""
        fig = go.Figure()

        # Dados do funil
        stages = ['Total no Funil', 'Em Progresso', 'Convertidos', 'Perdidos']
        values = [
            kpis['funil_total'],
            kpis['funil_progresso'],
            kpis['funil_convertidos'],
            kpis['funil_perdidos']
        ]
        colors = ['#3498db', '#3498db', '#2ecc71', '#e74c3c']

        fig.add_trace(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker_color=colors,
            connector={"line": {"color": "royalblue",
                                "dash": "dot", "width": 3}}
        ))

        fig.update_layout(
            title="Funil de Vendas por Status",
            font_size=12,
            height=400
        )

        return fig

    def criar_conversao_vendedor(self, df_vendedor):
        """Cria gráfico de taxa de conversão por vendedor"""
        if df_vendedor.empty:
            return go.Figure()

        fig = px.bar(
            df_vendedor,
            x='Vendedor',
            y='Taxa_Conversao',
            title='Taxa de Conversão por Vendedor (%)',
            color='Taxa_Conversao',
            color_continuous_scale='viridis'
        )

        fig.update_layout(
            xaxis_title="Vendedor",
            yaxis_title="Taxa de Conversão (%)",
            height=400
        )

        return fig

    def criar_pizza_status(self, df_filtrado):
        """Cria gráfico de pizza da distribuição de leads por status"""
        if df_filtrado.empty:
            return go.Figure()

        status_counts = df_filtrado['Status_Categoria'].value_counts()

        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title='Distribuição de Leads por Status',
            color=status_counts.index,
            color_discrete_map=self.cores
        )

        fig.update_layout(height=400)

        return fig

    def criar_performance_vendedor(self, df_vendedor):
        """Cria gráfico de performance por vendedor"""
        if df_vendedor.empty:
            return go.Figure()

        fig = go.Figure()

        # Total de leads
        fig.add_trace(go.Bar(
            name='Total de Leads',
            x=df_vendedor['Vendedor'],
            y=df_vendedor['Total_Leads'],
            marker_color='#3498db'
        ))

        # Vendas
        fig.add_trace(go.Bar(
            name='Vendas',
            x=df_vendedor['Vendedor'],
            y=df_vendedor['Vendas_Fechadas'],
            marker_color='#2ecc71'
        ))

        # Perdidos
        fig.add_trace(go.Bar(
            name='Perdidos',
            x=df_vendedor['Vendedor'],
            y=df_vendedor['Leads_Perdidos'],
            marker_color='#e74c3c'
        ))

        fig.update_layout(
            title='Performance por Vendedor',
            xaxis_title='Vendedor',
            yaxis_title='Quantidade',
            barmode='group',
            height=400
        )

        return fig

    def criar_leads_tempo(self, df_tempo):
        """Cria gráfico de leads criados ao longo do tempo"""
        if df_tempo.empty:
            return go.Figure()

        fig = px.line(
            df_tempo,
            x='Data',
            y='Quantidade',
            title='Leads Criados ao Longo do Tempo',
            markers=True
        )

        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Quantidade de Leads",
            height=400
        )

        return fig
