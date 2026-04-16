import streamlit as st
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from database.client import get_supabase_client
from utils.state import get_state

# --- Mock Data Otimizado e tipado com UUIDs fake para os IDs caso rode local (sem supabase) ---
MOCK_DATA = {
    'wallets': [
        {'id': str(uuid.uuid4()), 'nome_carteira': 'Pessoal', 'tipo': 'pessoal', 'saldo': 2500.00},
        {'id': str(uuid.uuid4()), 'nome_carteira': 'Casa', 'tipo': 'grupo', 'saldo': 1800.00},
        {'id': str(uuid.uuid4()), 'nome_carteira': 'Investimentos', 'tipo': 'pessoal', 'saldo': 15000.00}
    ]
}

# Add foreign keys às transações mockadas baseadas nos IDs dinâmicos:
mock_wallet_ids = [w['id'] for w in MOCK_DATA['wallets']]
MOCK_DATA['transactions'] = [
    {'id': str(uuid.uuid4()), 'wallet_id': mock_wallet_ids[0], 'valor': -150.00, 'categoria': 'Alimentação', 'descricao': 'Supermercado', 'data': '2026-04-15', 'is_fixo': False, 'status': 'pago'},
    {'id': str(uuid.uuid4()), 'wallet_id': mock_wallet_ids[0], 'valor': -89.90, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2026-04-14', 'is_fixo': False, 'status': 'pago'},
    {'id': str(uuid.uuid4()), 'wallet_id': mock_wallet_ids[1], 'valor': -350.00, 'categoria': 'Moradia', 'descricao': 'Aluguel', 'data': '2026-04-10', 'is_fixo': True, 'status': 'pago'},
    {'id': str(uuid.uuid4()), 'wallet_id': mock_wallet_ids[1], 'valor': -120.00, 'categoria': 'Utilidades', 'descricao': 'Energia', 'data': '2026-04-12', 'is_fixo': True, 'status': 'pendente'},
    {'id': str(uuid.uuid4()), 'wallet_id': mock_wallet_ids[2], 'valor': 500.00, 'categoria': 'Investimento', 'descricao': 'Aplicação mensal', 'data': '2026-04-05', 'is_fixo': True, 'status': 'pago'}
]


def load_wallets() -> List[Dict[str, Any]]:
    """Carrega as carteiras que o usuário atual tem acesso."""
    client = get_supabase_client()
    user = get_state("user")
    
    if client and user:
        try:
            # RLS vai filtrar automaticamente apenas o que ele tem acesso
            response = client.table("wallets").select("*").execute()
            return response.data
        except Exception as e:
            st.warning(f"Erro ao carregar carteiras do banco: {e}")
            return MOCK_DATA['wallets']
    return MOCK_DATA['wallets']


def load_transactions(wallet_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Carrega transações, filtrando por wallet_id se fornecido"""
    client = get_supabase_client()
    user = get_state("user")
    
    if client and user:
        try:
            query = client.table("transactions").select("*")
            if wallet_id:
                query = query.eq('wallet_id', wallet_id)
            # Ordena por data decrescente no banco (melhor performance: Pushdown)
            query = query.order('data', desc=True)
            response = query.execute()
            return response.data
        except Exception as e:
            st.warning(f"Erro ao carregar transações do banco: {e}")
            return filter_mock_transactions(wallet_id)
    
    return filter_mock_transactions(wallet_id)


def filter_mock_transactions(wallet_id: Optional[str] = None) -> List[Dict[str, Any]]:
    transactions = MOCK_DATA['transactions']
    if wallet_id:
        transactions = [t for t in transactions if str(t['wallet_id']) == str(wallet_id)]
    # Python in-memory sort para dados locais
    return sorted(transactions, key=lambda x: x['data'], reverse=True)


def register_transaction(wallet_id: str, valor: float, categoria: str, descricao: str, date: str, is_fixo: bool, status: str) -> bool:
    """Registra uma transação nova."""
    client = get_supabase_client()
    user = get_state("user")

    if client and user:
        try:
            client.table("transactions").insert({
                "wallet_id": wallet_id,
                "created_by": user.id,
                "valor": valor,
                "categoria": categoria,
                "descricao": descricao,
                "data": date,
                "is_fixo": is_fixo,
                "status": status
            }).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar transação: {e}")
            return False
            
    # Fallback pro MOCK só para UX instantânea sem reload
    MOCK_DATA['transactions'].insert(0, {
        'id': str(uuid.uuid4()),
        'wallet_id': wallet_id,
        'valor': valor,
        'categoria': categoria,
        'descricao': descricao,
        'data': date,
        'is_fixo': is_fixo,
        'status': status
    })
    return True
