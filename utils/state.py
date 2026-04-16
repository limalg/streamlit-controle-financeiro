import streamlit as st
from typing import Any, Optional

def init_state() -> None:
    """Inicializa as chaves padrão no st.session_state se não existirem."""
    defaults = {
        'authenticated': False,
        'user': None,
        'wallet_id': None,
        'carteira_atual': None,
        'apenas_fixos': False,
        'show_transfer': False,
        'show_close_month': False,
        'filter_date_start': None,
        'filter_date_end': None,
        'show_dialog': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_state(key: str, default: Any = None) -> Any:
    """Obtém um valor do state de forma segura."""
    return st.session_state.get(key, default)

def set_state(key: str, value: Any) -> None:
    """Define um valor no state."""
    st.session_state[key] = value

def clear_auth_state() -> None:
    """Limpa o estado de autenticação (Logout)."""
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.session_state['wallet_id'] = None
    st.session_state['carteira_atual'] = None
