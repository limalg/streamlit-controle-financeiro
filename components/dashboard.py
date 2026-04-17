import streamlit as st
import calendar
from datetime import datetime
import pandas as pd
import plotly.express as px


def render_kpi_cards(transacoes: list, carteira_atual: dict) -> None:
    """Renderiza cartões de métricas com design premium (color-coded)."""
    
    total_gastos = 0.0
    total_receitas = 0.0

    if transacoes:
        total_gastos = sum(float(t.get('valor', 0)) for t in transacoes if float(t.get('valor', 0)) < 0)
        total_receitas = sum(float(t.get('valor', 0)) for t in transacoes if float(t.get('valor', 0)) > 0)

    saldo_periodo = total_receitas + total_gastos
    
    st.markdown("""
        <style>
        .kpi-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 6px solid #ccc;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .kpi-label {
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .kpi-value {
            color: #212529;
            font-size: 1.5rem;
            font-weight: 800;
            margin: 0;
        }
        .card-receitas { border-left-color: #28a745; }
        .card-gastos { border-left-color: #dc3545; }
        .card-saldo { border-left-color: #007bff; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""<div class="kpi-card card-gastos"><p class="kpi-label">Despesas</p><p class="kpi-value">R$ {abs(total_gastos):,.2f}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card card-receitas"><p class="kpi-label">Receitas</p><p class="kpi-value">R$ {total_receitas:,.2f}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card card-saldo"><p class="kpi-label">Saldo do Período</p><p class="kpi-value">R$ {saldo_periodo:,.2f}</p></div>""", unsafe_allow_html=True)


def render_category_chart(transacoes: list) -> None:
    """Renderiza gráfico de gastos por categoria."""
    if not transacoes:
        st.info("ℹ️ Sem transações para exibir no gráfico de categorias.")
        return

    gastos_por_cat: dict[str, float] = {}
    for t in transacoes:
        val = float(t.get('valor', 0))
        cat = t.get('categoria', 'Outros')
        if val < 0:
            gastos_por_cat[cat] = gastos_por_cat.get(cat, 0) + abs(val)

    if not gastos_por_cat:
        st.info("ℹ️ Sem despesas registradas no período.")
        return

    st.subheader("📊 Gastos por Categoria")
    sorted_cats = dict(sorted(gastos_por_cat.items(), key=lambda x: x[1], reverse=True))
    
    df_chart = pd.DataFrame.from_dict(
        {"Categoria": list(sorted_cats.keys()), "Valor": list(sorted_cats.values())}
    )
    
    # Usando Plotly com paleta "Elegant & Smooth"
    fig = px.bar(df_chart, x="Categoria", y="Valor", color="Categoria",
                 color_discrete_sequence=px.colors.qualitative.Antique,
                 template="plotly_white")
    fig.update_layout(
        showlegend=False, 
        height=350, 
        margin=dict(l=20, r=20, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#555")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_monthly_trend_chart(transacoes: list) -> None:
    """Renderiza gráfico de tendência mensal (Gastos vs Receitas)."""
    if not transacoes:
        return

    st.subheader("🗓️ Tendência Mensal (Histórico)")
    df = pd.DataFrame(transacoes)
    
    if 'data' not in df.columns or 'valor' not in df.columns:
        return

    df['data'] = pd.to_datetime(df['data'])
    df['Mes'] = df['data'].dt.strftime('%Y-%m')
    
    df_receitas = df[df['valor'] > 0].groupby('Mes')['valor'].sum().rename('Receitas')
    df_gastos = df[df['valor'] < 0].groupby('Mes')['valor'].sum().abs().rename('Gastos')
    
    df_trend = pd.concat([df_receitas, df_gastos], axis=1).fillna(0).reset_index()
    df_trend = df_trend.sort_values('Mes')
    
    if df_trend.empty:
        st.info("ℹ️ Dados insuficientes para gerar tendência.")
        return

    fig = px.line(df_trend, x="Mes", y=["Receitas", "Gastos"], 
                  color_discrete_map={"Receitas": "#3ab09e", "Gastos": "#ed6b5a"},
                  markers=True, template="plotly_white")
    fig.update_layout(
        height=400, 
        legend_title=None, 
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_payment_method_pie(transacoes: list) -> None:
    """Pizza por método de pagamento (Apenas Despesas)."""
    if not transacoes: return
    
    # Conta apenas despesas
    df = pd.DataFrame(transacoes)
    df_despesas = df[df['valor'] < 0].copy()
    if df_despesas.empty:
        st.info("ℹ️ Sem despesas para gráfico por pagamento.")
        return

    if 'metodo_pagamento' not in df_despesas.columns:
        df_despesas['metodo_pagamento'] = 'não informado'

    df_pag = df_despesas.groupby('metodo_pagamento', as_index=False)['valor'].sum()
    df_pag['valor'] = df_pag['valor'].abs()
    df_pag.columns = ['Método', 'Valor']

    st.subheader("💳 Por Pagamento")
    fig = px.pie(df_pag, values='Valor', names='Método', 
                 color_discrete_sequence=px.colors.qualitative.Pastel2,
                 hole=0.4, template="plotly_white")
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=60), 
        height=350,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_fixed_cost_pie(transacoes: list) -> None:
    """Pizza por Fixo vs Variável (Apenas Despesas)."""
    if not transacoes: return
    
    df = pd.DataFrame(transacoes)
    df_despesas = df[df['valor'] < 0].copy()
    if df_despesas.empty: return

    if 'is_fixo' not in df_despesas.columns:
        df_despesas['is_fixo'] = False

    df_despesas['Tipo'] = df_despesas['is_fixo'].apply(lambda x: 'Custo Fixo' if x else 'Variável')
    df_fixo = df_despesas.groupby('Tipo', as_index=False)['valor'].sum()
    df_fixo['valor'] = df_fixo['valor'].abs()
    df_fixo.columns = ['Tipo', 'Valor']

    st.subheader("📌 Fixo vs Variável")
    fig = px.pie(df_fixo, values='Valor', names='Tipo',
                 color_discrete_map={'Custo Fixo': '#94a3b8', 'Variável': '#6366f1'},
                 hole=0.4, template="plotly_white")
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=60), 
        height=350,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_forecast(transacoes: list) -> None:
    """Renderiza a previsão mensal de despesas."""
    st.subheader("📈 Previsão de Gastos Mensais")

    hoje = datetime.now()
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_decorridos = hoje.day

    if transacoes:
        mes_atual = hoje.month
        ano_atual = hoje.year
        df = pd.DataFrame(transacoes)
        df['data'] = pd.to_datetime(df['data'])
        mask = (df['data'].dt.month == mes_atual) & (df['data'].dt.year == ano_atual)
        gastos_mes_atual = abs(df[mask & (df['valor'] < 0)]['valor'].sum())
        
        gasto_medio_diario = gastos_mes_atual / dias_decorridos if dias_decorridos > 0 else 0
        projecao_mes = gasto_medio_diario * dias_no_mes
    else:
        gasto_medio_diario = 0.0
        projecao_mes = 0.0

    st.info(f"💡 Baseado nos seus gastos de **{calendar.month_name[hoje.month]}**.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Gasto Médio Diário", f"R$ {gasto_medio_diario:,.2f}")
    with col2:
        st.metric("Projeção Final do Mês", f"R$ {projecao_mes:,.2f}")
