import streamlit as st

# Configuração inicial DEVE ser a primeira chamada do Streamlit
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.state import init_state, get_state, set_state
from components.auth import render_login
from components.sidebar import render_sidebar
from components.dashboard import render_kpi_cards, render_forecast, render_category_chart, render_monthly_trend_chart
from components.transactions_table import render_transaction_table
from database.repository import load_wallets, load_transactions



def main():
    """Ponto de entrada principal da aplicação modular."""
    
    # Inicia estado padrão
    init_state()
    
    # Verifica Autenticação
    if not get_state("authenticated"):
        render_login()
        return

    # -- Fluxo da Aplicação Autenticada --
    carteiras = load_wallets()
    render_sidebar(carteiras)
    
    wallet_id = get_state("wallet_id")
    carteira_atual = get_state("carteira_atual")
    apenas_fixos = get_state("apenas_fixos")
    
    # Cabeçalho da página principal
    if carteira_atual:
        st.header(f"Dashboard - {carteira_atual.get('nome_carteira', 'Desconhecida')}")
    else:
        st.header("Dashboard Geral")
        
    st.divider()

    # Carrega transações baseadas na carteira atual
    transacoes_originais = load_transactions(wallet_id)
    
    # 3. LÓGICA DE FILTRAGEM GLOBAL (Data)
    import pandas as pd
    df_temp = pd.DataFrame(transacoes_originais)
    
    date_start = get_state("filter_date_start")
    date_end = get_state("filter_date_end")
    
    if not df_temp.empty and date_start and date_end:
        df_temp['data'] = pd.to_datetime(df_temp['data']).dt.date
        mask = (df_temp['data'] >= date_start) & (df_temp['data'] <= date_end)
        transacoes_filtradas = df_temp[mask].to_dict('records')
    else:
        transacoes_filtradas = transacoes_originais

    # Processa e renderiza KPIs (Respeita Filtro)
    render_kpi_cards(transacoes_filtradas, carteira_atual)
    st.divider()

    # Gráfico de gastos por categoria (Respeita Filtro)
    render_category_chart(transacoes_filtradas)
    st.divider()

    # Gráfico de tendência mensal (Ignora Datas do Filtro, Respeita Carteira)
    render_monthly_trend_chart(transacoes_originais)
    st.divider()
    
    # Processa e renderiza a Tabela (Respeita Filtro)
    render_transaction_table(transacoes_filtradas)
    st.divider()
    
    # Processa e renderiza a Previsão (Respeita Filtro)
    render_forecast(transacoes_filtradas)
    



if __name__ == "__main__":
    main()