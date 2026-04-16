import streamlit as st
from datetime import datetime

def render_kpi_cards(transacoes: list, carteira_atual: dict) -> None:
    """Renderiza os cartões superiores de métricas: Gastos, Receitas, Saldo Atual."""
    col1, col2, col3 = st.columns(3)
    
    total_gastos = 0.0
    total_receitas = 0.0
    
    if transacoes:
        total_gastos = sum(float(t.get('valor', 0)) for t in transacoes if float(t.get('valor', 0)) < 0)
        total_receitas = sum(float(t.get('valor', 0)) for t in transacoes if float(t.get('valor', 0)) > 0)
        
    with col1:
        st.metric("Total Gastos", f"R$ {abs(total_gastos):,.2f}")
        
    with col2:
        st.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
        
    with col3:
        saldo_atual = total_receitas + total_gastos
        
        # Considera o saldo que estava instanciado na carteira em database vs transações exibidas
        saldo_anterior = float(carteira_atual.get('saldo', 0)) if carteira_atual else 0.0
        delta = saldo_atual - saldo_anterior
        
        # Streamlit st.metric suporta delta colorido automático
        st.metric("Saldo Atual", f"R$ {saldo_atual:,.2f}", delta=f"R$ {delta:,.2f}" if carteira_atual else None)


def render_forecast(transacoes: list) -> None:
    """Renderiza a previsão mensal de despesas."""
    st.subheader("📈 Previsão do Mês")
    
    hoje = datetime.now()
    dias_no_mes = 30
    dias_decorridos = hoje.day
    
    if transacoes:
        gastos_mes = sum(float(t.get('valor', 0)) for t in transacoes if float(t.get('valor', 0)) < 0)
        gasto_medio_diario = abs(gastos_mes) / dias_decorridos if dias_decorridos > 0 else 0
        projecao_mes = gasto_medio_diario * dias_no_mes
    else:
        gasto_medio_diario = 0.0
        projecao_mes = 0.0
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Gasto Médio Diário", f"R$ {gasto_medio_diario:,.2f}")
        
    with col2:
        st.metric("Projeção Mensal (Despesas)", f"R$ {projecao_mes:,.2f}")
