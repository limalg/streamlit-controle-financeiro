import streamlit as st
import pandas as pd
from database.repository import register_transaction, delete_transaction, update_transaction
from utils.state import get_state

CATEGORIAS = ["Alimentação", "Transporte", "Moradia", "Lazer", "Investimento", "Utilidades", "Salário", "Outros"]
ROWS_PER_PAGE = 15


@st.dialog("➕ Nova Transação")
def new_transaction_dialog(wallet_id: str):
    """Diálogo reativo para nova transação."""
    # O método de pagamento fica fora do form para garantir o rerun imediato ao clicar
    st.write("**Pagamento**")
    metodo = st.segmented_control(
        "Selecione o método", 
        ["Dinheiro", "Débito", "Crédito"], 
        default="Dinheiro",
        key="new_transaction_payment_method", # Chave estável para evitar flicker
        label_visibility="collapsed"
    )
    
    # Lógica de Parcelamento (reativa)
    total_parcelas = 1
    valor_final = 0.0
    modo_valor = "Valor da Parcela"
    
    if metodo == "Crédito":
        col_parc1, col_parc2 = st.columns([1, 1.5])
        with col_parc1:
            total_parcelas = st.number_input("Parcelas", min_value=1, max_value=48, value=1)
        with col_parc2:
            if total_parcelas > 1:
                modo_valor = st.radio(
                    "Tipo de Valor", 
                    ["Total a dividir", "Valor da Parcela"], 
                    horizontal=True
                )
        
        valor_input = st.number_input("Valor", min_value=0.01, step=0.01)
        
        if total_parcelas > 1 and modo_valor == "Total a dividir":
            valor_final = valor_input 
            st.caption(f"💡 Será gerado {total_parcelas} parcelas de R$ {valor_input/total_parcelas:.2f}")
        else:
            valor_final = valor_input * total_parcelas
    else:
        valor_final = st.number_input("Valor", min_value=0.01, step=0.01)

    # O Form agora contém apenas os campos que não alteram o layout
    with st.form("form_new_transaction_internal"):
        desc = st.text_input("Descrição", placeholder="Ex: Notebook, Almoço...")
        cat = st.selectbox("Categoria", CATEGORIAS)

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            tipo_transacao = st.selectbox("Tipo", ["Despesa", "Receita"])
        with c_opt2:
            status = st.selectbox("Status", ["pago", "pendente"])

        c_date1, c_date2 = st.columns(2)
        with c_date1:
            data = st.date_input("Data")
        with c_date2:
            is_fixo = st.checkbox("Custo Fixo")

        submitted = st.form_submit_button("Salvar Transação", width="stretch", type="primary")
        if submitted:
            val_total = -valor_final if tipo_transacao == "Despesa" else valor_final
            success = register_transaction(
                wallet_id=wallet_id,
                valor=val_total,
                categoria=cat,
                descricao=desc,
                date=str(data),
                is_fixo=is_fixo,
                status=status,
                metodo_pagamento=metodo.lower() if metodo else "dinheiro",
                total_parcelas=int(total_parcelas)
            )
            if success:
                st.success("Transação adicionada!")
                st.session_state["show_dialog"] = None
                st.rerun()


@st.dialog("✏️ Gerenciar Transação")
def edit_delete_dialog(transacao: dict, row_idx: int):
    trans_id = str(transacao.get("id", ""))
    tab_edit, tab_delete = st.tabs(["✏️ Editar", "🗑️ Excluir"])

    with tab_edit:
        val_atual = float(transacao.get("valor", 0))
        tipo_default = "Receita" if val_atual >= 0 else "Despesa"

        with st.form("form_edit_transaction"):
            desc = st.text_input("Descrição", value=str(transacao.get("descricao", "")))
            cat_idx = CATEGORIAS.index(transacao["categoria"]) if transacao.get("categoria") in CATEGORIAS else 0
            cat = st.selectbox("Categoria", CATEGORIAS, index=cat_idx)

            c1, c2 = st.columns(2)
            with c1:
                valor = st.number_input("Valor", min_value=0.01, step=0.01, value=abs(val_atual))
            with c2:
                tipo = st.selectbox("Tipo", ["Despesa", "Receita"], index=1 if tipo_default == "Receita" else 0)

            c3, c4 = st.columns(2)
            with c3:
                try:
                    data_atual = pd.to_datetime(transacao.get("data")).date()
                except Exception:
                    data_atual = pd.Timestamp.now().date()
                data = st.date_input("Data", value=data_atual)
            with c4:
                is_fixo = st.checkbox("Custo Fixo", value=bool(transacao.get("is_fixo", False)))
                status_opts = ["pago", "pendente"]
                status_idx = status_opts.index(transacao["status"]) if transacao.get("status") in status_opts else 0
                status = st.selectbox("Status", status_opts, index=status_idx)

            col_cancel, col_save = st.columns(2)
            with col_cancel:
                cancelled = st.form_submit_button("Cancelar", width="stretch")
            with col_save:
                saved = st.form_submit_button("Salvar", width="stretch", type="primary")

            if cancelled:
                st.session_state["dismissed_row"] = row_idx
                st.rerun()

            if saved:
                val_final = -valor if tipo == "Despesa" else valor
                if update_transaction(trans_id, val_final, cat, desc, str(data), is_fixo, status):
                    st.session_state.pop("dismissed_row", None)
                    st.rerun()

    with tab_delete:
        st.warning(f"Isso vai excluir **{transacao.get('descricao', '')}** permanentemente.")
        
        group_id = transacao.get("group_id")
        delete_all = False
        if group_id:
            st.info("📦 Esta transação faz parte de um parcelamento.")
            delete_all = st.checkbox("Excluir todas as parcelas restantes deste grupo?", value=False)

        col1, col2 = st.columns(2)
        if col1.button("Cancelar", width="stretch"):
            st.session_state["dismissed_row"] = row_idx
            st.rerun()
        if col2.button("🗑️ Confirmar Exclusão", type="primary", width="stretch"):
            if delete_transaction(trans_id, delete_all_remaining=delete_all, group_id=group_id):
                st.session_state.pop("dismissed_row", None)
                st.rerun()


def render_transaction_table(transacoes: list) -> None:
    """Renderiza a tabela usando transações já filtradas enviadas pelo app.py."""
    col_title, col_btn = st.columns([0.8, 0.2])
    with col_title:
        st.subheader("📝 Transações no Período")
    with col_btn:
        wallet_id = get_state("wallet_id")
        if wallet_id and st.button("➕ Adicionar", type="primary", width="stretch"):
            st.session_state["show_dialog"] = "new"
            st.rerun()

    if not transacoes:
        st.info("📭 Nenhuma transação encontrada no período selecionado.")
        return

    df_page = pd.DataFrame(transacoes)

    if 'data' in df_page.columns:
        df_page['data'] = pd.to_datetime(df_page['data'], errors='coerce')
    if 'valor' in df_page.columns:
        df_page['valor'] = pd.to_numeric(df_page['valor'], errors='coerce')

    df_page = df_page.sort_values('data', ascending=False).reset_index(drop=True)

    total_rows = len(df_page)

    # Paginação
    total_pages = max(1, (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)
    current_page = st.session_state.get("table_page", 1)
    current_page = min(current_page, total_pages)

    start = (current_page - 1) * ROWS_PER_PAGE
    end = start + ROWS_PER_PAGE
    df_view_page = df_page.iloc[start:end].copy()
    df_view_page = df_view_page.reset_index(drop=True)

    df_view_page.insert(0, 'Ação', '✏️ / 🗑️')
    colunas_validas = [c for c in ['Ação', 'data', 'metodo_pagamento', 'descricao', 'categoria', 'valor', 'status'] if c in df_view_page.columns]
    df_view = df_view_page[colunas_validas].copy()

    # Legenda + info de paginação
    col_caption, col_info = st.columns([0.6, 0.4])
    with col_caption:
        st.caption("👆 Clique em uma linha para editar ou excluir")
    with col_info:
        st.caption(f"Exibindo {start + 1}–{min(end, total_rows)} de {total_rows} transações")

    event = st.dataframe(
        df_view,
        column_config={
            "Ação": st.column_config.TextColumn("Ação", width="small"),
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "metodo_pagamento": st.column_config.TextColumn("Pagamento"),
            "descricao": st.column_config.TextColumn("Descrição"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "status": st.column_config.TextColumn("Status")
        },
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Controles de navegação de página
    if total_pages > 1:
        nav_cols = st.columns([1, 2, 1])
        with nav_cols[0]:
            if st.button("◀ Anterior", disabled=(current_page <= 1), key="pg_prev"):
                st.session_state["table_page"] = current_page - 1
                st.session_state.pop("dismissed_row", None)
                st.rerun()
        with nav_cols[1]:
            st.markdown(f"<p style='text-align:center;margin-top:6px'>Página {current_page} / {total_pages}</p>", unsafe_allow_html=True)
        with nav_cols[2]:
            if st.button("Próxima ▶", disabled=(current_page >= total_pages), key="pg_next"):
                st.session_state["table_page"] = current_page + 1
                st.session_state.pop("dismissed_row", None)
                st.rerun()

    # Controle centralizado de diálogos para evitar o erro "Only one dialog"
    if st.session_state.get("show_dialog") == "new":
        new_transaction_dialog(wallet_id)
    elif event and getattr(event, 'selection', None) and len(event.selection.rows) > 0:
        row_idx = event.selection.rows[0]
        selected_trans = df_view_page.iloc[row_idx].to_dict()
        edit_delete_dialog(selected_trans, row_idx)
    else:
        st.session_state.pop("dismissed_row", None)
