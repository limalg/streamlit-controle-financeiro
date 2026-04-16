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
    transacoes = load_transactions(wallet_id)
    
    # Aplica filtro dinâmico
    if apenas_fixos and transacoes:
        transacoes = [t for t in transacoes if isinstance(t, dict) and t.get('is_fixo')]
        
    # Processa e renderiza KPIs
    render_kpi_cards(transacoes, carteira_atual)
    st.divider()

    # Gráfico de gastos por categoria
    render_category_chart(transacoes)
    st.divider()

    # Gráfico de tendência mensal (anos e meses)
    render_monthly_trend_chart(transacoes)
    st.divider()
    
    # Processa e renderiza a Tabela
    render_transaction_table(transacoes)
    st.divider()
    
    # Processa e renderiza a Previsão
    render_forecast(transacoes)
    



if __name__ == "__main__":
    main()