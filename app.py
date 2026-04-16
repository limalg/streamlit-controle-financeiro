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
from components.dashboard import render_kpi_cards, render_forecast
from components.transactions_table import render_transaction_table
from database.repository import load_wallets, load_transactions

def render_transfer_modal(carteiras: list) -> None:
    """Renderiza a simulação de modal de transferência (na sidebar) se ativo."""
    if get_state('show_transfer'):
        with st.sidebar:
            st.divider()
            st.subheader("🔄 Transferência")
            
            # Formata opções para os selectors
            opcoes = {c['nome_carteira']: c['id'] for c in carteiras if isinstance(c, dict)}
            
            origem = st.selectbox("Origem:", options=list(opcoes.keys()))
            destino = st.selectbox("Destino:", options=[k for k in opcoes.keys() if k != origem])
            valor = st.number_input("Valor:", min_value=0.01, step=0.01)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirmar", key="btn_confirm_transfer"):
                    st.success(f"Transferência de R$ {valor:,.2f} realizada!")
                    set_state('show_transfer', False)
                    # Força rerun para limpar estado de tela
                    st.rerun()
            with col2:
                if st.button("Cancelar", key="btn_cancel_transfer"):
                    set_state('show_transfer', False)
                    st.rerun()


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
    
    # Processa e renderiza a Tabela
    render_transaction_table(transacoes)
    st.divider()
    
    # Processa e renderiza a Previsão
    render_forecast(transacoes)
    
    # Renderiza possíveis modais de ações baseados no State
    render_transfer_modal(carteiras)
    

if __name__ == "__main__":
    main()