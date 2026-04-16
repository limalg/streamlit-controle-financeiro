import streamlit as st
import pandas as pd

def render_transaction_table(transacoes: list) -> None:
    """Renderiza a tabela de transações utilizando st.dataframe moderno."""
    st.subheader("📝 Últimas Transações")
    
    if not transacoes:
        st.info("📭 Nenhuma transação encontrada.")
        return
        
    df = pd.DataFrame(transacoes)
    
    # Tratando colunas
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
    if 'valor' in df.columns:
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
    df = df.sort_values('data', ascending=False)
    
    # Seleção estrita das colunas de visualização
    colunas_validas = [col for col in ['data', 'descricao', 'categoria', 'valor', 'status'] if col in df.columns]
    df_view = df[colunas_validas].copy()
    
    # Renderização da Dataframe otimizada do Streamlit
    st.dataframe(
        df_view,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "valor": st.column_config.NumberColumn(
                "Valor",
                format="R$ %.2f"
            ),
            "status": st.column_config.TextColumn("Status")
        },
        use_container_width=True,
        hide_index=True
    )
