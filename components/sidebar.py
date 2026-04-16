import streamlit as st
from utils.state import get_state, set_state
from components.auth import render_logout_button

def render_sidebar(carteiras: list) -> None:
    """
    Renderiza a sidebar incluindo a escolha da carteira e filtros.
    Recebe a lista de carteiras carregada do repository.
    """
    with st.sidebar:
        st.title("💰 Controle Financeiro")
        
        if not carteiras:
            st.warning("Nenhuma carteira disponível")
            set_state("wallet_id", None)
            set_state("carteira_atual", None)
            render_logout_button()
            return
            
        opcoes_carteiras = {}
        for c in carteiras:
            nome = c.get('nome_carteira', 'Sem nome')
            tipo = c.get('tipo', 'pessoal')
            emoji = '🔒' if tipo == 'pessoal' else '👥'
            opcoes_carteiras[f"{nome} ({emoji})"] = c.get('id')
            
        carteira_selecionada = st.selectbox(
            "Selecionar Carteira:",
            options=list(opcoes_carteiras.keys()),
            index=0
        )
        
        wallet_id = opcoes_carteiras[carteira_selecionada]
        carteira_atual = next((c for c in carteiras if c.get('id') == wallet_id), None)
        
        set_state("wallet_id", wallet_id)
        set_state("carteira_atual", carteira_atual)
        
        st.divider()
        
        if carteira_atual:
            st.subheader(f"{carteira_atual['nome_carteira']}")
            if carteira_atual['tipo'] == 'pessoal':
                st.caption("🔒 Carteira Pessoal")
            else:
                st.caption("👥 Carteira Compartilhada")
                
            saldo = float(carteira_atual.get('saldo', 0))
            st.metric("Saldo Disponível", f"R$ {saldo:,.2f}")
            
        st.divider()
        
        st.subheader("Filtros")
        
        # Lendo estado anterior para manter entre rerenders
        atual_filtro = get_state("apenas_fixos", False)
        novo_filtro = st.toggle("📋 Apenas Custos Fixos", value=atual_filtro)
        set_state("apenas_fixos", novo_filtro)
        
        st.divider()
        render_logout_button()

