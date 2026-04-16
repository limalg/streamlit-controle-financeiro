# Resumo do Projeto: App de Controle Financeiro com Múltiplas Carteiras

## Visão Geral
Sistema de gestão financeira pessoal/familiar com foco na gestão de múltiplas carteiras (wallets) através de interface Streamlit e backend Supabase.

## Público-Alvo
- Uso pessoal e familiar (2-50 usuários)
- Gestão de finanças individuais e compartilhadas

## Stack Tecnológica
- **Frontend:** Streamlit
- **Backend:** Supabase
- **Banco de Dados:** PostgreSQL (via Supabase)
- **Autenticação:** Supabase Auth
- **Gerenciamento de Estado:** Streamlit Session State
- **Visualização de Dados:** Streamlit Components
- **Design:** Tailwind CSS
- **Git:** GitHub


## Funcionalidades Principais
1. **Seletor de Carteiras na Sidebar** - Filtragem dinâmica de dados
2. **Dashboard Contextual** - Visualização específica por carteira
3. **Transferência entre Carteiras** - Movimentação de fundos
4. **Filtro de Custos Fixos** - Destaque de gastos recorrentes
5. **Fechamento Mensal** - Encerramento do período financeiro

## Estrutura de Dados (Supabase)
```sql
Users(id, email, nome)
Wallets(id, nome_carteira, tipo)
Wallet_Members(wallet_id, user_id) 
Transactions(id, wallet_id, valor, categoria, is_fixo, status)
```

## Diferenciais
- Visualização condicional (ícone de cadeado para privado, avatares para compartilhado)
- Mudança de contexto mental entre diferentes orçamentos
- Foco em usabilidade para uso pessoal/familiar

## Próximos Passos Sugeridos
1. Configuração inicial com Supabase + Streamlit(Via GitHub)
2. Implementação do seletor de carteiras na sidebar
3. Desenvolvimento do dashboard contextual
4. Fluxo de transferência entre carteiras

---
*Documento gerado para handoff de implementação*