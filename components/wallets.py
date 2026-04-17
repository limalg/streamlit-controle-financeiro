import streamlit as st
from database.repository import (
    load_wallets, create_wallet, update_wallet, delete_wallet, 
    generate_wallet_invite_code, join_wallet_by_code,
    get_wallet_members, remove_wallet_member
)
from utils.state import get_state

def render_wallet_management():
    """Página central de gestão de contas e compartilhamento via códigos."""
    st.header("💸 Gerenciar Minhas Contas")
    st.markdown("Crie, edite ou entre em carteiras compartilhadas através de códigos.")

    # 1. SEÇÃO DE ENTRAR EM CONTA EXISTENTE
    with st.expander("📦 Já tem um código? Entrar em uma conta", expanded=False):
        col_code, col_join = st.columns([0.7, 0.3])
        with col_code:
            join_code = st.text_input("Cole o código aqui", placeholder="Ex: FAMILIA-LIMA", label_visibility="collapsed")
        with col_join:
            if st.button("🚪 Entrar na Conta", use_container_width=True, type="primary"):
                if join_code:
                    if join_wallet_by_code(join_code):
                        st.rerun()
                else:
                    st.error("Digite um código válido.")

    st.divider()

    # 2. BOTÃO NOVA CARTEIRA
    if st.button("➕ Nova Conta Própria", type="secondary"):
        st.session_state["show_new_wallet_dialog"] = True

    if st.session_state.get("show_new_wallet_dialog"):
        render_new_wallet_dialog()

    st.divider()

    # 3. LISTAGEM DE CARTEIRAS
    carteiras = load_wallets()
    user = get_state("user")

    if not carteiras:
        st.info("Você ainda não possui carteiras vinculadas.")
        return

    for wallet in carteiras:
        with st.container(border=True):
            col_info, col_actions = st.columns([0.7, 0.3])
            
            with col_info:
                emoji = '🔒' if wallet.get('tipo') == 'pessoal' else '👥'
                st.subheader(f"{emoji} {wallet.get('nome_carteira')}")
                st.caption(f"Tipo: {wallet.get('tipo').capitalize()} | ID: {wallet.get('id')[:8]}...")
                if user and wallet.get('owner_id') == user.id:
                    st.success("Você é o proprietário")
                else:
                    st.info("Carteira compartilhada")

            with col_actions:
                # Apenas o dono pode configurar/convidar
                if user and wallet.get('owner_id') == user.id:
                    if st.button("⚙️ Configurar / Convidar", key=f"edit_w_{wallet['id']}"):
                        st.session_state[f"manage_wallet_{wallet['id']}"] = not st.session_state.get(f"manage_wallet_{wallet['id']}", False)
                else:
                    if st.button("🚪 Sair da Conta", key=f"leave_{wallet['id']}"):
                        if remove_wallet_member(wallet['id'], user.id):
                            st.success("Você saiu da conta.")
                            st.rerun()

            # Seção de Configuração Expandida
            if st.session_state.get(f"manage_wallet_{wallet['id']}"):
                st.divider()
                tab_invite, tab_edit, tab_members = st.tabs(["🤝 Convidar", "✏️ Editar Conta", "👥 Membros"])
                
                with tab_invite:
                    st.write("### 🔑 Código de Acesso")
                    st.caption("Crie um código amigável e envie para quem você quer convidar.")
                    
                    current_code = wallet.get('invite_code')
                    if current_code:
                        st.info(f"Código Atual: **{current_code}**")
                        st.caption(f"Válido até: {wallet.get('invite_expires_at')[:10]}")
                        if st.button("Copia Código", key=f"copy_{wallet['id']}"):
                            st.success("Código copiado! (Simulado)")
                    
                    with st.form(key=f"form_code_{wallet['id']}"):
                        custom_code = st.text_input("Criar código personalizado (Opcional)", placeholder="Ex: VIAGEM-2024")
                        if st.form_submit_button("Gerar / Atualizar Código"):
                            if generate_wallet_invite_code(wallet['id'], custom_code):
                                st.success("Novo código gerado!")
                                st.rerun()

                with tab_edit:
                    with st.form(key=f"form_edit_{wallet['id']}"):
                        new_name = st.text_input("Nome da Carteira", value=wallet['nome_carteira'])
                        new_type = st.selectbox("Tipo", ["pessoal", "grupo"], 
                                             index=0 if wallet['tipo'] == 'pessoal' else 1)
                        
                        if st.form_submit_button("Salvar Alterações", use_container_width=True):
                            if update_wallet(wallet['id'], new_name, new_type):
                                st.success("Atualizada!")
                                st.rerun()

                    if st.button("🗑️ EXCLUIR CONTA DEFINITIVAMENTE", key=f"btn_del_{wallet['id']}", type="secondary"):
                        if delete_wallet(wallet['id']):
                            st.success("Excluída!")
                            st.rerun()

                with tab_members:
                    st.write("#### Membros com Acesso")
                    members = get_wallet_members(wallet['id'])
                    if not members:
                        st.caption("Nenhum membro convidado ainda.")
                    else:
                        for m in members:
                            m_user = m.get('users', {})
                            col_m1, col_m2 = st.columns([0.8, 0.2])
                            with col_m1:
                                st.write(f"- {m_user.get('nome')} ({m_user.get('email')})")
                            with col_m2:
                                if st.button("Remover", key=f"rm_m_{wallet['id']}_{m['user_id']}"):
                                    if remove_wallet_member(wallet['id'], m['user_id']):
                                        st.rerun()

@st.dialog("Nova Carteira")
def render_new_wallet_dialog():
    """Diálogo para criação de nova wallet."""
    nome = st.text_input("Nome da Carteira", placeholder="Ex: Casa, Viagem, etc.")
    tipo = st.selectbox("Tipo", ["pessoal", "grupo"])
    saldo = st.number_input("Saldo Inicial", value=0.0, step=100.0)
    
    if st.button("Criar Conta", type="primary", use_container_width=True):
        if nome:
            if create_wallet(nome, tipo, saldo):
                st.success("Sucesso!")
                st.session_state["show_new_wallet_dialog"] = False
                st.rerun()
        else:
            st.error("Nome é obrigatório.")
