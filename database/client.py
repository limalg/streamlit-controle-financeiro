import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """
    Inicializa a conexão com o Supabase utilizando st.secrets ou variáveis de ambiente.
    Utiliza cache do Streamlit para manter a conexão aberta em memoization e só recriar quando necessário.
    """
    try:
        url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
        key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))
        
        # Como o .toml gerencia mock/dados placehold, validamos se está usando a URL real do supabase
        if not url or not key or "sua_url" in url:
            return None
            
        return create_client(url, key)
    except Exception as e:
        print(f"Erro ao inicializar Supabase: {e}")
        return None
