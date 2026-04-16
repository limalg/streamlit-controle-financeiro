import streamlit as st
import calendar
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
        saldo_anterior = float(carteira_atual.get('saldo', 0)) if carteira_atual else 0.0
        delta = saldo_atual - saldo_anterior
        st.metric("Saldo Atual", f"R$ {saldo_atual:,.2f}", delta=f"R$ {delta:,.2f}" if carteira_atual else None)


def render_category_chart(transacoes: list) -> None:
    """Renderiza gráfico de gastos por categoria."""
    if not transacoes:
        return

    gastos_por_cat: dict[str, float] = {}
    for t in transacoes:
        val = float(t.get('valor', 0))
        cat = t.get('categoria', 'Outros')
        if val < 0:
            gastos_por_cat[cat] = gastos_por_cat.get(cat, 0) + abs(val)

    if not gastos_por_cat:
        return

    st.subheader("📊 Gastos por Categoria")

    # Ordena por valor decrescente
    sorted_cats = dict(sorted(gastos_por_cat.items(), key=lambda x: x[1], reverse=True))

    # Usa st.bar_chart nativo (leve, sem dependência extra)
    import pandas as pd
    df_chart = pd.DataFrame.from_dict(
        {"Categoria": list(sorted_cats.keys()), "R$": list(sorted_cats.values())}
    )
    st.bar_chart(df_chart.set_index("Categoria"), height=260, color="#4a9eff")


def render_monthly_trend_chart(transacoes: list) -> None:
    """Renderiza gráfico de tendência mensal (Gastos vs Receitas)."""
    if not transacoes:
        return

    st.subheader("🗓️ Tendência Mensal (Gastos vs Receitas)")

    import pandas as pd
    df = pd.DataFrame(transacoes)
    
    if 'data' not in df.columns or 'valor' not in df.columns:
        return

    df['data'] = pd.to_datetime(df['data'])
    # Cria coluna Mês/Ano (YYYY-MM) para agrupamento
    df['Mes'] = df['data'].dt.strftime('%Y-%m')
    
    # Agrupa por mês e tipo (Gastos/Receitas)
    df_receitas = df[df['valor'] > 0].groupby('Mes')['valor'].sum().rename('Receitas')
    df_gastos = df[df['valor'] < 0].groupby('Mes')['valor'].sum().abs().rename('Gastos')
    
    df_trend = pd.concat([df_receitas, df_gastos], axis=1).fillna(0).sort_index()
    
    if df_trend.empty:
        st.info("ℹ️ Dados insuficientes para gerar tendência.")
        return

    # Gráfico de barras combinadas ou áreas
    st.line_chart(df_trend, height=300, color=["#2ecc71", "#e74c3c"])


def render_forecast(transacoes: list) -> None:
    """Renderiza a previsão mensal de despesas."""
    st.subheader("📈 Previsão do Mês")

    hoje = datetime.now()
    # Número real de dias do mês atual
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
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
