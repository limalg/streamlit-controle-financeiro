import streamlit as st
from utils.state import get_state, set_state
from components.auth import render_logout_button
from datetime import date as date_type

def render_sidebar(carteiras: list) -> None:
    """Sidebar centralizada para wallet e filtros globais."""
    with st.sidebar:
        st.title("💰 Carteira")
        
        if not carteiras:
            st.warning("Nenhuma carteira disponível")
            set_state("wallet_id", None)
            set_state("carteira_atual", None)
            render_logout_button()
            return
            
        # 1. SELEÇÃO DE CARTEIRA
        opcoes_nomes = []
        id_map = {}
        for c in carteiras:
            emoji = '🔒' if c.get('tipo') == 'pessoal' else '👥'
            label = f"{emoji} {c.get('nome_carteira', 'Sem nome')}"
            opcoes_nomes.append(label)
            id_map[label] = c.get('id')
            
        # Determina o index atual baseado no state
        current_wallet_id = get_state("wallet_id")
        current_index = 0
        if current_wallet_id:
            for i, label in enumerate(opcoes_nomes):
                if id_map[label] == current_wallet_id:
                    current_index = i
                    break

        wallet_label = st.selectbox(
            "Alternar Conta:",
            options=opcoes_nomes,
            index=current_index,
            key="sb_wallet_select"
        )
        
        selected_id = id_map[wallet_label]
        carteira_atual = next((c for c in carteiras if c.get('id') == selected_id), None)
        
        # Sincroniza estado
        set_state("wallet_id", selected_id)
        set_state("carteira_atual", carteira_atual)
        
        if carteira_atual:
            saldo = float(carteira_atual.get('saldo', 0))
            st.metric("Saldo Disponível", f"R$ {saldo:,.2f}")
            
        st.divider()
        
        # 2. FILTRO DE PERÍODO (Sempre Aberto no Sidebar)
        st.subheader("🗓️ Período")
        hoje = date_type.today()
        
        # Inicialização local caso ainda não esteja no state
        if st.session_state.get("filter_date_start") is None:
            st.session_state["filter_date_start"] = hoje.replace(day=1)
        if st.session_state.get("filter_date_end") is None:
            st.session_state["filter_date_end"] = hoje

        st.date_input("Início:", key="filter_date_start")
        st.date_input("Fim:", key="filter_date_end")

        if st.button("Limpar Filtro", key="sb_reset_dates", width="stretch"):
            st.session_state["filter_date_start"] = hoje.replace(day=1)
            st.session_state["filter_date_end"] = hoje
            st.rerun()

        st.divider()
        render_logout_button()
