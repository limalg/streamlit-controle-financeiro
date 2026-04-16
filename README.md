# 🎯 App de Controle Financeiro com Múltiplas Carteiras

Sistema de gestão financeira pessoal/familiar com foco na gestão de múltiplas carteiras através de interface Streamlit e backend Supabase.

## 🚀 Funcionalidades

- **Seletor de Carteiras**: Mude entre carteiras pessoais e compartilhadas na sidebar
- **Dashboard Contextual**: Visualização específica por carteira selecionada
- **Transferência entre Carteiras**: Movimentação de fundos entre diferentes carteiras
- **Filtro de Custos Fixos**: Destaque automático de gastos recorrentes
- **Previsão Financeira**: Projeção de gastos mensais baseada em média diária
- **Fechamento Mensal**: Botão para encerramento do período financeiro

## 🛠️ Tecnologias

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **Estilo**: CSS integrado do Streamlit
- **Deploy**: Render / Streamlit Cloud / local

## 📦 Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd streamlit-controle-financeiro
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows

pip install -r requirements.txt
```

3. Configure o Supabase:
   - Crie uma conta em [supabase.com](https://supabase.com)
   - Crie um novo projeto
   - Execute o SQL de setup (veja abaixo)

4. Configure as variáveis de ambiente:
```bash
export SUPABASE_URL="sua_url_do_supabase"
export SUPABASE_KEY="sua_chave_do_supabase"
```

Ou edite `.streamlit/secrets.toml`

## 🗃️ Setup do Banco de Dados

Execute este SQL no editor SQL do Supabase:

```sql
-- Tabela de usuários (integra com Auth do Supabase)
CREATE TABLE IF NOT EXISTS users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Tabela de carteiras
CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    nome_carteira TEXT NOT NULL,
    tipo TEXT CHECK (tipo IN ('pessoal', 'grupo')) DEFAULT 'pessoal',
    saldo DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Tabela de membros das carteiras (para carteiras compartilhadas)
CREATE TABLE IF NOT EXISTS wallet_members (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES wallets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    UNIQUE(wallet_id, user_id)
);

-- Tabela de transações
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES wallets(id) ON DELETE CASCADE,
    valor DECIMAL(10,2) NOT NULL,
    categoria TEXT NOT NULL,
    descricao TEXT,
    data DATE NOT NULL DEFAULT CURRENT_DATE,
    is_fixo BOOLEAN DEFAULT FALSE,
    status TEXT CHECK (status IN ('pago', 'pendente')) DEFAULT 'pendente',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Dados de exemplo
INSERT INTO wallets (nome_carteira, tipo, saldo) VALUES 
('Pessoal', 'pessoal', 2500.00),
('Casa', 'grupo', 1800.00),
('Investimentos', 'pessoal', 15000.00);

INSERT INTO transactions (wallet_id, valor, categoria, descricao, data, is_fixo, status) VALUES 
(1, -150.00, 'Alimentação', 'Supermercado', '2026-04-15', FALSE, 'pago'),
(1, -89.90, 'Transporte', 'Combustível', '2026-04-14', FALSE, 'pago'),
(2, -350.00, 'Moradia', 'Aluguel', '2026-04-10', TRUE, 'pago'),
(2, -120.00, 'Utilidades', 'Energia', '2026-04-12', TRUE, 'pendente'),
(3, 500.00, 'Investimento', 'Aplicação mensal', '2026-04-05', TRUE, 'pago');
```

## 🎮 Como Usar

1. **Selecionar Carteira**: Use o dropdown na sidebar para escolher qual carteira visualizar
2. **Ver Dashboard**: O dashboard mostra métricas e transações da carteira selecionada
3. **Filtrar Custos Fixos**: Ative o toggle para ver apenas gastos recorrentes
4. **Transferir**: Clique em "Transferir entre Carteiras" para mover dinheiro
5. **Fechar Mês**: Use o botão para finalizar o período mensal

## 🚀 Deploy

### Opção 1: Streamlit Cloud (Recomendado)
1. Faça push para o GitHub
2. Conecte no [Streamlit Cloud](https://streamlit.io/cloud)
3. Configure as secrets no painel do Streamlit

### Opção 2: Render
1. Crie um arquivo `render.yaml`
2. Configure as variáveis de ambiente
3. Deploy automático

### Opção 3: Local
```bash
streamlit run app.py
```

## 🎨 Personalização

- Modifique as cores editando o CSS do Streamlit
- Adicione novas categorias na tabela de transações
- Implemente autenticação completa com Supabase Auth
- Adicione gráficos mais elaborados com Plotly/Altair

## 📈 Próximas Funcionalidades

- [ ] Autenticação completa de usuários
- [ ] Gráficos interativos com Plotly
- [ ] Relatórios PDF automatizados
- [ ] Notificações por email
- [ ] Integração com bancos via API
- [ ] App mobile com Reflex

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

---

**Desenvolvido com ❤️ usando Streamlit + Supabase**