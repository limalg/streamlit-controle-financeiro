import streamlit as st
from database.client import get_supabase_client
from utils.state import set_state, get_state, clear_auth_state

class SupabaseUser:
    """Mock user object to allow testing without Supabase initialized"""
    def __init__(self, id, email):
        self.id = id
        self.email = email

def render_login():
    """Renderiza a tela de Login ou Cadastro"""
    client = get_supabase_client()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("💰 Controle Financeiro")
        st.subheader("Login / Cadastro")
        
        # Se não há client supabase ativo com banco real
        if not client:
            st.info("⚠️ Modo Local (Supabase não configurado plenamente). Entrando em modo mock.")
            if st.button("Entrar no Modo Teste", use_container_width=True):
                set_state("user", SupabaseUser("mock-uuid-9999", "teste@mock.com"))
                set_state("authenticated", True)
                st.rerun()
            return
            
        tab_login, tab_register = st.tabs(["🔒 Entrar", "📝 Cadastrar"])
        
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    try:
                        res = client.auth.sign_in_with_password({"email": email, "password": password})
                        if res.user:
                            set_state("user", res.user)
                            set_state("authenticated", True)
                            st.success("Login realizado com sucesso!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro no login: {str(e).split(':')[-1] if ':' in str(e) else str(e)}")
                        
        with tab_register:
            with st.form("register_form"):
                reg_nome = st.text_input("Nome Completo")
                reg_email = st.text_input("Email")
                reg_password = st.text_input("Senha", type="password")
                reg_password_confirm = st.text_input("Confirmar Senha", type="password")
                reg_submit = st.form_submit_button("Cadastrar", use_container_width=True)
                
                if reg_submit:
                    if reg_password != reg_password_confirm:
                        st.error("As senhas não conferem.")
                    elif len(reg_password) < 6:
                        st.error("Senha precisa de pelo menos 6 caracteres.")
                    else:
                        try:
                            # Passa metadados pro trigger SQL poder pegar
                            res = client.auth.sign_up({
                                "email": reg_email, 
                                "password": reg_password,
                                "options": {
                                    "data": { "full_name": reg_nome }
                                }
                            })
                            st.success("Cadastro realizado! Você já pode entrar.")
                        except Exception as e:
                            st.error(f"Erro no cadastro: {e}")

def render_logout_button():
    """Renderiza o botão de Sair na sidebar"""
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        client = get_supabase_client()
        if client:
            try:
                client.auth.sign_out()
            except:
                pass
        clear_auth_state()
        st.rerun()
