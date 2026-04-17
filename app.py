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
from components.wallets import render_wallet_management
from database.repository import load_wallets, load_transactions


def main():
    """Roteador principal da aplicação multipáginas."""
    
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
    active_page = get_state("active_page", "📑 Transações")
    
    # Carregamento e filtragem de dados
    transacoes_originais = load_transactions(wallet_id)
    
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

    # -- ROTEAMENTO DE PÁGINAS --
    
    if active_page == "📑 Transações":
        st.header(f"📑 Transações - {carteira_atual.get('nome_carteira', '') if carteira_atual else ''}")
        # KPIs Premium
        render_kpi_cards(transacoes_filtradas, carteira_atual)
        st.divider()
        # Tabela
        render_transaction_table(transacoes_filtradas)

    elif active_page == "📊 Gráficos":
        st.header("📊 Inteligência Financeira")
        
        # 1. Tendência (Empilhado)
        render_monthly_trend_chart(transacoes_originais)
        st.divider()

        # 2. Categorias (Empilhado)
        render_category_chart(transacoes_filtradas)
        st.divider()

        # 3. Pizzas de Detalhamento (Lado a Lado)
        col_pie1, col_pie2 = st.columns(2)
        with col_pie1:
            from components.dashboard import render_payment_method_pie
            render_payment_method_pie(transacoes_filtradas)
        with col_pie2:
            from components.dashboard import render_fixed_cost_pie
            render_fixed_cost_pie(transacoes_filtradas)
        
    elif active_page == "📈 Projeção":
        st.header("📈 Projeções e Metas")
        render_forecast(transacoes_filtradas)

    elif active_page == "💸 Contas":
        render_wallet_management()

    st.divider()


if __name__ == "__main__":
    main()