-- --------------------------------------------------------
-- 🎯 Schema Otimizado para Supabase
-- Inclui Autenticação Automática e Row Level Security (RLS)
-- --------------------------------------------------------

-- 1. EXTENSIONS (Necessário para geração de UUIDs se usar offline)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. TABELAS (Semelhante ao anterior mas com referências exatas e preparadas p/ RLS)

CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    nome TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

CREATE TABLE IF NOT EXISTS public.wallets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    owner_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    nome_carteira TEXT NOT NULL,
    tipo TEXT CHECK (tipo IN ('pessoal', 'grupo')) DEFAULT 'pessoal',
    saldo DECIMAL(12,2) DEFAULT 0.00,
    invite_code TEXT UNIQUE,
    invite_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Tabela associativa para carteiras do tipo "grupo"
CREATE TABLE IF NOT EXISTS public.wallet_members (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    wallet_id UUID REFERENCES public.wallets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    UNIQUE(wallet_id, user_id)
);

CREATE TABLE IF NOT EXISTS public.transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    wallet_id UUID REFERENCES public.wallets(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    valor DECIMAL(12,2) NOT NULL,
    categoria TEXT NOT NULL,
    descricao TEXT,
    data DATE NOT NULL DEFAULT CURRENT_DATE,
    is_fixo BOOLEAN DEFAULT FALSE,
    status TEXT CHECK (status IN ('pago', 'pendente')) DEFAULT 'pendente',
    metodo_pagamento TEXT CHECK (metodo_pagamento IN ('dinheiro', 'debito', 'credito')) DEFAULT 'dinheiro',
    parcela_atual INTEGER DEFAULT 1,
    total_parcelas INTEGER DEFAULT 1,
    group_id UUID, -- Usado para identificar parcelas da mesma compra
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

CREATE TABLE IF NOT EXISTS public.pending_invites (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    wallet_id UUID REFERENCES public.wallets(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    invited_by UUID REFERENCES public.users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
    UNIQUE(wallet_id, email)
);

-- --------------------------------------------------------
-- 3. AUTOMATIZAÇÃO: Criação de usuário na tabela "public.users" 
-- ao registrar no "auth.users" nativo do Supabase.
-- --------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
DECLARE
    invite_record RECORD;
BEGIN
  -- 1. Cria o usuário na tabela public
  INSERT INTO public.users (id, email, nome)
  VALUES (
    new.id, 
    new.email, 
    COALESCE(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1))
  );
  
  -- 2. Busca e resgata convites pendentes (Não expirados)
  FOR invite_record IN 
      SELECT wallet_id FROM public.pending_invites 
      WHERE LOWER(email) = LOWER(new.email) AND expires_at > NOW()
  LOOP
      INSERT INTO public.wallet_members (wallet_id, user_id)
      VALUES (invite_record.wallet_id, new.id)
      ON CONFLICT DO NOTHING;
  END LOOP;

  -- 3. Limpa convites processados
  DELETE FROM public.pending_invites WHERE LOWER(email) = LOWER(new.email);

  -- 4. Cria uma carteira "Pessoal" padrão para o novo usuário
  INSERT INTO public.wallets (owner_id, nome_carteira, tipo, saldo)
  VALUES (new.id, 'Carteira Pessoal', 'pessoal', 0.00);
  
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger disparada quando o usuário criar a conta no auth.users do Supabase
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();


-- --------------------------------------------------------
-- 4. RLS - ROW LEVEL SECURITY (Segurança de Linha)
-- Bloqueia a leitura/escrita não autorizada das tabelas via API.
-- --------------------------------------------------------

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallet_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- users: Usuário pode ver apenas seus dados (e talvez dos membros dos seus grupos, simplificado pro mesmo user)
CREATE POLICY "Usuário vê a si próprio" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Usuário edita a si próprio" ON public.users FOR UPDATE USING (auth.uid() = id);

-- wallets: O usuário pode ver a carteira se for dono (owner_id) ou membro
CREATE POLICY "Acesso à carteiras: Dono ou Membro" ON public.wallets FOR SELECT
USING (
  auth.uid() = owner_id 
  OR id IN (SELECT wallet_id FROM public.wallet_members WHERE user_id = auth.uid())
);
CREATE POLICY "Inserção na carteira apenas próprio usr" ON public.wallets FOR INSERT WITH CHECK (auth.uid() = owner_id);
CREATE POLICY "Atualização/Deleção de carteiras pelo dono" ON public.wallets FOR ALL USING (auth.uid() = owner_id);

-- wallet_members: o usuário só vê sua própria membresia (evita recursão infinita no banco)
CREATE POLICY "Membros da carteira visiveis" ON public.wallet_members FOR SELECT USING (
  user_id = auth.uid()
);

-- transactions: O usuário pode ver/inserir em transações cujas carteiras aparecem pra ele
-- Como a engine do PostgreSQL já roda a Policy de 'wallets' silenciosamente quando fazemos o select, 
-- basta validar se ele tem resposta pro ID da carteira envolvida. Evita recursão infinita!
CREATE POLICY "Ver e Inserir Transacoes" ON public.transactions FOR ALL USING (
  wallet_id IN (SELECT id FROM public.wallets)
);
