from datetime import datetime, date as date_type
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any, Optional
import uuid

from database.client import get_supabase_client
from utils.state import get_state

# --- Mock Data com UUIDs fixos (constantes) para não quebrar relações no hot-reload ---
MOCK_WALLET_1 = "00000000-0000-0000-0000-000000000001"
MOCK_WALLET_2 = "00000000-0000-0000-0000-000000000002"
MOCK_WALLET_3 = "00000000-0000-0000-0000-000000000003"

MOCK_DATA = {
    'wallets': [
        {'id': MOCK_WALLET_1, 'nome_carteira': 'Pessoal', 'tipo': 'pessoal', 'saldo': 2500.00},
        {'id': MOCK_WALLET_2, 'nome_carteira': 'Casa', 'tipo': 'grupo', 'saldo': 1800.00},
        {'id': MOCK_WALLET_3, 'nome_carteira': 'Investimentos', 'tipo': 'pessoal', 'saldo': 15000.00}
    ],
    'transactions': [
        {'id': '831d054d-0453-432a-bc96-df30ba219198', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -280.45, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2026-04-14', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5b1bebee-4eca-44ef-9447-9dcba333e660', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 1779.61, 'categoria': 'Investimento', 'descricao': 'Fundo Imobiliário', 'data': '2026-04-14', 'is_fixo': False, 'status': 'pago'},
        {'id': '43aa4148-356c-4f90-8e7c-ed59ff9b207e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -461.35, 'categoria': 'Alimentação', 'descricao': 'iFood', 'data': '2026-04-12', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'afda58e3-0c4f-4eb0-bb2f-37053e1654e8', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -56.88, 'categoria': 'Outros', 'descricao': 'Farmácia', 'data': '2026-04-12', 'is_fixo': True, 'status': 'pago'},
        {'id': 'ba3defd5-896f-40e8-bbc4-7a192801452a', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -52.48, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2026-04-11', 'is_fixo': True, 'status': 'pago'},
        {'id': 'c7344931-1372-46a4-9968-07b140cc5363', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -298.53, 'categoria': 'Outros', 'descricao': 'Educação', 'data': '2026-04-09', 'is_fixo': True, 'status': 'pendente'},
        {'id': '33f6a62c-611a-47af-99dc-a21b465f6c82', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -347.92, 'categoria': 'Outros', 'descricao': 'Assinatura Netflix', 'data': '2026-04-09', 'is_fixo': True, 'status': 'pendente'},
        {'id': '26e67923-3e1b-4f99-90f9-a8648e429188', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -155.03, 'categoria': 'Lazer', 'descricao': 'Livros', 'data': '2026-04-08', 'is_fixo': False, 'status': 'pendente'},
        {'id': '0ef60741-6e84-4860-9112-9c98ba9067b7', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -278.47, 'categoria': 'Utilidades', 'descricao': 'Celular', 'data': '2026-04-04', 'is_fixo': True, 'status': 'pendente'},
        {'id': '02237d80-5a3d-4c31-b3b3-855c3cfa8742', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -461.59, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2026-04-04', 'is_fixo': False, 'status': 'pago'},
        {'id': '6fa371c6-2c96-4bb6-b184-4835695ab823', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -268.03, 'categoria': 'Lazer', 'descricao': 'Livros', 'data': '2026-03-31', 'is_fixo': False, 'status': 'pendente'},
        {'id': '77890f84-7548-43d7-8e10-639a0994f388', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -188.07, 'categoria': 'Utilidades', 'descricao': 'Gás', 'data': '2026-03-31', 'is_fixo': True, 'status': 'pago'},
        {'id': '86cf640c-3ee7-47b2-bd7d-02482e98fa90', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -265.48, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2026-03-29', 'is_fixo': False, 'status': 'pago'},
        {'id': '1f9fb5c6-663f-42a1-94f4-5264b97f0a67', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -412.35, 'categoria': 'Transporte', 'descricao': 'Estacionamento', 'data': '2026-03-27', 'is_fixo': True, 'status': 'pendente'},
        {'id': '06c6e7a2-f942-498c-8438-fb1c58ced6e2', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -108.79, 'categoria': 'Utilidades', 'descricao': 'Internet', 'data': '2026-03-26', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'f7d2426f-4dc0-4b57-9d7a-751bd5d93375', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -82.69, 'categoria': 'Utilidades', 'descricao': 'Celular', 'data': '2026-03-26', 'is_fixo': True, 'status': 'pago'},
        {'id': '20e0d54c-1123-455b-b9d3-6e7e59b2bd2b', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -117.89, 'categoria': 'Alimentação', 'descricao': 'Restaurante', 'data': '2026-03-23', 'is_fixo': False, 'status': 'pendente'},
        {'id': '7ad13b82-628d-4ad1-9457-3a1ecb98bce1', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -113.68, 'categoria': 'Lazer', 'descricao': 'Games', 'data': '2026-03-21', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5017df88-3482-4114-8700-f9bdcf3be7ac', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -246.54, 'categoria': 'Lazer', 'descricao': 'Cinema', 'data': '2026-03-12', 'is_fixo': False, 'status': 'pago'},
        {'id': 'fd61725b-09fc-4c40-9a3b-285b0d00f68e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -347.88, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2026-03-11', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'e12e1713-d34e-4f59-9993-90d4fbb1b1c6', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -230.14, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2026-03-09', 'is_fixo': True, 'status': 'pago'},
        {'id': '5cb4e650-7170-4949-93e1-325bdf9c6d31', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -79.91, 'categoria': 'Utilidades', 'descricao': 'Celular', 'data': '2026-03-08', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'da056961-0b5c-4394-bb9f-52a0a25ae023', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -461.34, 'categoria': 'Moradia', 'descricao': 'Condomínio', 'data': '2026-03-02', 'is_fixo': True, 'status': 'pago'},
        {'id': 'aa43ab1a-fae1-455b-860f-90236a6db90e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -337.89, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2026-02-28', 'is_fixo': True, 'status': 'pendente'},
        {'id': '5b7190f8-b39b-4497-ae66-88def7d81232', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -341.67, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2026-02-27', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'bd9ba8d4-53bf-4702-8a9d-19598f82f80c', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -223.75, 'categoria': 'Lazer', 'descricao': 'Games', 'data': '2026-02-22', 'is_fixo': False, 'status': 'pago'},
        {'id': 'd735072c-80ed-4fb1-9024-5d5b76611394', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -281.39, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2026-02-22', 'is_fixo': True, 'status': 'pago'},
        {'id': '2f782c5f-08f3-4e4b-b016-17b70f074465', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -125.79, 'categoria': 'Utilidades', 'descricao': 'Água', 'data': '2026-02-21', 'is_fixo': True, 'status': 'pago'},
        {'id': '6b59ef9b-8f15-46eb-8e50-f8ca7e0b5034', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': 2132.84, 'categoria': 'Salário', 'descricao': 'Salário Mensal', 'data': '2026-02-20', 'is_fixo': False, 'status': 'pago'},
        {'id': '9bd8e815-560b-410a-b44c-35cdb3b3dd7e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -465.34, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2026-02-14', 'is_fixo': True, 'status': 'pago'},
        {'id': '20c4ef1c-f236-407b-89ba-dcdfd8ccf9a6', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -278.49, 'categoria': 'Moradia', 'descricao': 'Reforma', 'data': '2026-02-12', 'is_fixo': False, 'status': 'pendente'},
        {'id': '25cd9d49-43c3-4d76-9286-9a2dfc889f41', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -250.79, 'categoria': 'Moradia', 'descricao': 'Decoração', 'data': '2026-02-10', 'is_fixo': False, 'status': 'pago'},
        {'id': 'ddc388bc-c632-4467-8152-4043b433464a', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -426.33, 'categoria': 'Transporte', 'descricao': 'Manutenção Carro', 'data': '2026-02-09', 'is_fixo': True, 'status': 'pago'},
        {'id': '569a4734-d035-4204-ae87-0b1e389d0f1c', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -341.67, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2026-02-08', 'is_fixo': False, 'status': 'pendente'},
        {'id': '438d2fde-da87-43ca-93ca-a3ea956e185e', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -81.79, 'categoria': 'Moradia', 'descricao': 'Decoração', 'data': '2026-02-07', 'is_fixo': False, 'status': 'pendente'},
        {'id': '71f849be-d06e-4cc3-9092-234b95fcd91c', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -72.68, 'categoria': 'Utilidades', 'descricao': 'Celular', 'data': '2026-02-05', 'is_fixo': True, 'status': 'pendente'},
        {'id': '831d054d-0453-432a-bc96-df30ba219198', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -380.45, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2026-01-24', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5b1bebee-4eca-44ef-9447-9dcba333e660', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 2779.61, 'categoria': 'Investimento', 'descricao': 'Fundo Imobiliário', 'data': '2026-01-20', 'is_fixo': False, 'status': 'pago'},
        {'id': 'e12e1713-d34e-4f59-9993-90d4fbb1b1c6', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -130.14, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2026-01-09', 'is_fixo': True, 'status': 'pago'},
        {'id': '5cb4e650-7170-4949-93e1-325bdf9c6d31', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -109.91, 'categoria': 'Utilidades', 'descricao': 'Celular', 'data': '2026-01-08', 'is_fixo': True, 'status': 'pendente'},
        {'id': '6fa371c6-2c96-4bb6-b184-4835695ab823', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -168.03, 'categoria': 'Lazer', 'descricao': 'Livros', 'data': '2025-12-31', 'is_fixo': False, 'status': 'pendente'},
        {'id': '77890f84-7548-43d7-8e10-639a0994f388', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -108.07, 'categoria': 'Utilidades', 'descricao': 'Gás', 'data': '2025-12-31', 'is_fixo': True, 'status': 'pago'},
        {'id': '86cf640c-3ee7-47b2-bd7d-02482e98fa90', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -165.48, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2025-12-29', 'is_fixo': False, 'status': 'pago'},
        {'id': '5017df88-3482-4114-8700-f9bdcf3be7ac', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -146.54, 'categoria': 'Lazer', 'descricao': 'Cinema', 'data': '2025-12-12', 'is_fixo': False, 'status': 'pago'},
        {'id': 'aa43ab1a-fae1-455b-860f-90236a6db90e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -137.89, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2025-12-01', 'is_fixo': True, 'status': 'pendente'},
        {'id': '5b7190f8-b39b-4497-ae66-88def7d81232', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -141.67, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2025-11-27', 'is_fixo': True, 'status': 'pendente'},
        {'id': '2f782c5f-08f3-4e4b-b016-17b70f074465', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -105.79, 'categoria': 'Utilidades', 'descricao': 'Água', 'data': '2025-11-21', 'is_fixo': True, 'status': 'pago'},
        {'id': 'd735072c-80ed-4fb1-9024-5d5b76611394', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -181.39, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2025-11-20', 'is_fixo': True, 'status': 'pago'},
        {'id': '43aa4148-356c-4f90-8e7c-ed59ff9b207e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -161.35, 'categoria': 'Alimentação', 'descricao': 'iFood', 'data': '2025-11-12', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'afda58e3-0c4f-4eb0-bb2f-37053e1654e8', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -16.88, 'categoria': 'Outros', 'descricao': 'Farmácia', 'data': '2025-11-12', 'is_fixo': True, 'status': 'pago'},
        {'id': 'ba3defd5-896f-40e8-bbc4-7a192801452a', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -12.48, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2025-11-11', 'is_fixo': True, 'status': 'pago'},
        {'id': '25cd9d49-43c3-4d76-9286-9a2dfc889f41', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -150.79, 'categoria': 'Moradia', 'descricao': 'Decoração', 'data': '2025-11-10', 'is_fixo': False, 'status': 'pago'},
        {'id': '20c4ef1c-f236-407b-89ba-dcdfd8ccf9a6', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -178.49, 'categoria': 'Moradia', 'descricao': 'Reforma', 'data': '2025-11-02', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5091da58-4f19-4f1e-a4e8-8cf042113630', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -123.29, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2025-10-17', 'is_fixo': True, 'status': 'pago'},
        {'id': '7c2b7557-c6be-406c-817c-5aaef41dfb7d', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -156.1, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2025-10-07', 'is_fixo': True, 'status': 'pendente'},
        {'id': '30f0f3d4-6daf-428c-8e9c-7791195f1a95', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -101.17, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2025-10-06', 'is_fixo': True, 'status': 'pago'},
        {'id': '2ec3c6b2-75af-4ae6-9520-fad68aa1c3e9', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -183.49, 'categoria': 'Alimentação', 'descricao': 'Restaurante', 'data': '2025-10-03', 'is_fixo': False, 'status': 'pendente'},
        {'id': 'c87d02b3-e6eb-434c-b60b-657c8a23370b', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -121.18, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2025-10-03', 'is_fixo': True, 'status': 'pago'},
        {'id': '9980874f-1efc-451c-b87a-40dc6148b849', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -177.81, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2025-09-16', 'is_fixo': True, 'status': 'pago'},
        {'id': 'dfcd0eb9-c54c-42a9-9395-b8d38b98ff89', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 2715.0, 'categoria': 'Salário', 'descricao': 'Freelance', 'data': '2025-09-15', 'is_fixo': False, 'status': 'pago'},
        {'id': '831d054d-0453-432a-bc96-df30ba219198', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -180.45, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2025-08-14', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5b1bebee-4eca-44ef-9447-9dcba333e660', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 1379.61, 'categoria': 'Investimento', 'descricao': 'Fundo Imobiliário', 'data': '2025-08-14', 'is_fixo': False, 'status': 'pago'},
        {'id': '28488408-09e8-45b8-a942-491d7bed9070', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -133.54, 'categoria': 'Outros', 'descricao': 'Presente', 'data': '2025-08-13', 'is_fixo': True, 'status': 'pendente'},
        {'id': '7b30deda-fe17-426c-af71-6f5a805ef370', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -198.55, 'categoria': 'Alimentação', 'descricao': 'Feira', 'data': '2025-08-08', 'is_fixo': False, 'status': 'pendente'},
        {'id': '43aa4148-356c-4f90-8e7c-ed59ff9b207e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -161.35, 'categoria': 'Alimentação', 'descricao': 'iFood', 'data': '2025-07-12', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'afda58e3-0c4f-4eb0-bb2f-37053e1654e8', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -26.88, 'categoria': 'Outros', 'descricao': 'Farmácia', 'data': '2025-07-12', 'is_fixo': True, 'status': 'pago'},
        {'id': 'ba3defd5-896f-40e8-bbc4-7a192801452a', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -32.48, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2025-07-11', 'is_fixo': True, 'status': 'pago'},
        {'id': '6fa371c6-2c96-4bb6-b184-4835695ab823', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -148.03, 'categoria': 'Lazer', 'descricao': 'Livros', 'data': '2025-06-30', 'is_fixo': False, 'status': 'pendente'},
        {'id': '77890f84-7548-43d7-8e10-639a0994f388', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -108.07, 'categoria': 'Utilidades', 'descricao': 'Gás', 'data': '2025-06-30', 'is_fixo': True, 'status': 'pago'},
        {'id': '86cf640c-3ee7-47b2-bd7d-02482e98fa90', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -165.48, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2025-06-29', 'is_fixo': False, 'status': 'pago'},
        {'id': '5017df88-3482-4114-8700-f9bdcf3be7ac', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -16.54, 'categoria': 'Lazer', 'descricao': 'Cinema', 'data': '2025-06-12', 'is_fixo': False, 'status': 'pago'},
        {'id': 'aa43ab1a-fae1-455b-860f-90236a6db90e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -137.89, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2025-06-01', 'is_fixo': True, 'status': 'pendente'},
        {'id': '5b7190f8-b39b-4497-ae66-88def7d81232', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -141.67, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2025-05-27', 'is_fixo': True, 'status': 'pendente'},
        {'id': '2f782c5f-08f3-4e4b-b016-17b70f074465', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -105.79, 'categoria': 'Utilidades', 'descricao': 'Água', 'data': '2025-05-21', 'is_fixo': True, 'status': 'pago'},
        {'id': 'd735072c-80ed-4fb1-9024-5d5b76611394', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -181.39, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2025-05-20', 'is_fixo': True, 'status': 'pago'},
        {'id': '5091da58-4f19-4f1e-a4e8-8cf042113630', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -123.29, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2025-04-17', 'is_fixo': True, 'status': 'pago'},
        {'id': '7c2b7557-c6be-406c-817c-5aaef41dfb7d', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -156.1, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2025-04-07', 'is_fixo': True, 'status': 'pendente'},
        {'id': '30f0f3d4-6daf-428c-8e9c-7791195f1a95', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -101.17, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2025-04-06', 'is_fixo': True, 'status': 'pago'},
        {'id': '2ec3c6b2-75af-4ae6-9520-fad68aa1c3e9', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -183.49, 'categoria': 'Alimentação', 'descricao': 'Restaurante', 'data': '2025-04-03', 'is_fixo': False, 'status': 'pendente'},
        {'id': 'c87d02b3-e6eb-434c-b60b-657c8a23370b', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -121.18, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2025-04-03', 'is_fixo': True, 'status': 'pago'},
        {'id': '25cd9d49-43c3-4d76-9286-9a2dfc889f41', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -150.79, 'categoria': 'Moradia', 'descricao': 'Decoração', 'data': '2025-03-10', 'is_fixo': False, 'status': 'pago'},
        {'id': '20c4ef1c-f236-407b-89ba-dcdfd8ccf9a6', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -178.49, 'categoria': 'Moradia', 'descricao': 'Reforma', 'data': '2025-03-02', 'is_fixo': False, 'status': 'pendente'},
        {'id': 'dfcd0eb9-c54c-42a9-9395-b8d38b98ff89', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 2715.0, 'categoria': 'Salário', 'descricao': 'Freelance', 'data': '2025-02-15', 'is_fixo': False, 'status': 'pago'},
        {'id': '831d054d-0453-432a-bc96-df30ba219198', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -180.45, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2025-01-14', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5b1bebee-4eca-44ef-9447-9dcba333e660', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 1379.61, 'categoria': 'Investimento', 'descricao': 'Fundo Imobiliário', 'data': '2025-01-14', 'is_fixo': False, 'status': 'pago'},
        {'id': '28488408-09e8-45b8-a942-491d7bed9070', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -133.54, 'categoria': 'Outros', 'descricao': 'Presente', 'data': '2025-01-13', 'is_fixo': True, 'status': 'pendente'},
        {'id': '7b30deda-fe17-426c-af71-6f5a805ef370', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -198.55, 'categoria': 'Alimentação', 'descricao': 'Feira', 'data': '2025-01-08', 'is_fixo': False, 'status': 'pendente'},
        {'id': '6fa371c6-2c96-4bb6-b184-4835695ab823', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -148.03, 'categoria': 'Lazer', 'descricao': 'Livros', 'data': '2024-12-31', 'is_fixo': False, 'status': 'pendente'},
        {'id': '77890f84-7548-43d7-8e10-639a0994f388', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -108.07, 'categoria': 'Utilidades', 'descricao': 'Gás', 'data': '2024-12-31', 'is_fixo': True, 'status': 'pago'},
        {'id': '86cf640c-3ee7-47b2-bd7d-02482e98fa90', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -165.48, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2024-12-29', 'is_fixo': False, 'status': 'pago'},
        {'id': '5017df88-3482-4114-8700-f9bdcf3be7ac', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -146.54, 'categoria': 'Lazer', 'descricao': 'Cinema', 'data': '2024-12-12', 'is_fixo': False, 'status': 'pago'},
        {'id': 'aa43ab1a-fae1-455b-860f-90236a6db90e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -137.89, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2024-12-01', 'is_fixo': True, 'status': 'pendente'},
        {'id': '5b7190f8-b39b-4497-ae66-88def7d81232', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -141.67, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2024-11-27', 'is_fixo': True, 'status': 'pendente'},
        {'id': '2f782c5f-08f3-4e4b-b016-17b70f074465', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -105.79, 'categoria': 'Utilidades', 'descricao': 'Água', 'data': '2024-11-21', 'is_fixo': True, 'status': 'pago'},
        {'id': 'd735072c-80ed-4fb1-9024-5d5b76611394', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -181.39, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2024-11-20', 'is_fixo': True, 'status': 'pago'},
        {'id': '43aa4148-356c-4f90-8e7c-ed59ff9b207e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -161.35, 'categoria': 'Alimentação', 'descricao': 'iFood', 'data': '2024-11-12', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'afda58e3-0c4f-4eb0-bb2f-37053e1654e8', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -16.88, 'categoria': 'Outros', 'descricao': 'Farmácia', 'data': '2024-11-12', 'is_fixo': True, 'status': 'pago'},
        {'id': 'ba3defd5-896f-40e8-bbc4-7a192801452a', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -12.48, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2024-11-11', 'is_fixo': True, 'status': 'pago'},
        {'id': '25cd9d49-43c3-4d76-9286-9a2dfc889f41', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -150.79, 'categoria': 'Moradia', 'descricao': 'Decoração', 'data': '2024-11-10', 'is_fixo': False, 'status': 'pago'},
        {'id': '20c4ef1c-f236-407b-89ba-dcdfd8ccf9a6', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -178.49, 'categoria': 'Moradia', 'descricao': 'Reforma', 'data': '2024-11-02', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5091da58-4f19-4f1e-a4e8-8cf042113630', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -123.29, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2024-10-17', 'is_fixo': True, 'status': 'pago'},
        {'id': '7c2b7557-c6be-406c-817c-5aaef41dfb7d', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -156.1, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2024-10-07', 'is_fixo': True, 'status': 'pendente'},
        {'id': '30f0f3d4-6daf-428c-8e9c-7791195f1a95', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -101.17, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2024-10-06', 'is_fixo': True, 'status': 'pago'},
        {'id': '2ec3c6b2-75af-4ae6-9520-fad68aa1c3e9', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -183.49, 'categoria': 'Alimentação', 'descricao': 'Restaurante', 'data': '2024-10-03', 'is_fixo': False, 'status': 'pendente'},
        {'id': 'c87d02b3-e6eb-434c-b60b-657c8a23370b', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -121.18, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2024-10-03', 'is_fixo': True, 'status': 'pago'},
        {'id': '9980874f-1efc-451c-b87a-40dc6148b849', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -177.81, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2024-09-16', 'is_fixo': True, 'status': 'pago'},
        {'id': 'dfcd0eb9-c54c-42a9-9395-b8d38b98ff89', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 2715.0, 'categoria': 'Salário', 'descricao': 'Freelance', 'data': '2024-09-15', 'is_fixo': False, 'status': 'pago'},
        {'id': '831d054d-0453-432a-bc96-df30ba219198', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -180.45, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2024-08-14', 'is_fixo': False, 'status': 'pendente'},
        {'id': '5b1bebee-4eca-44ef-9447-9dcba333e660', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': 1379.61, 'categoria': 'Investimento', 'descricao': 'Fundo Imobiliário', 'data': '2024-08-14', 'is_fixo': False, 'status': 'pago'},
        {'id': '28488408-09e8-45b8-a942-491d7bed9070', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -133.54, 'categoria': 'Outros', 'descricao': 'Presente', 'data': '2024-08-13', 'is_fixo': True, 'status': 'pendente'},
        {'id': '7b30deda-fe17-426c-af71-6f5a805ef370', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -198.55, 'categoria': 'Alimentação', 'descricao': 'Feira', 'data': '2024-08-08', 'is_fixo': False, 'status': 'pendente'},
        {'id': '43aa4148-356c-4f90-8e7c-ed59ff9b207e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -161.35, 'categoria': 'Alimentação', 'descricao': 'iFood', 'data': '2024-07-12', 'is_fixo': True, 'status': 'pendente'},
        {'id': 'afda58e3-0c4f-4eb0-bb2f-37053e1654e8', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -26.88, 'categoria': 'Outros', 'descricao': 'Farmácia', 'data': '2024-07-12', 'is_fixo': True, 'status': 'pago'},
        {'id': 'ba3defd5-896f-40e8-bbc4-7a192801452a', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -32.48, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2024-07-11', 'is_fixo': True, 'status': 'pago'},
        {'id': '6fa371c6-2c96-4bb6-b184-4835695ab823', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -148.03, 'categoria': 'Lazer', 'descricao': 'Livros', 'data': '2024-06-30', 'is_fixo': False, 'status': 'pendente'},
        {'id': '77890f84-7548-43d7-8e10-639a0994f388', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -108.07, 'categoria': 'Utilidades', 'descricao': 'Gás', 'data': '2024-06-30', 'is_fixo': True, 'status': 'pago'},
        {'id': '86cf640c-3ee7-47b2-bd7d-02482e98fa90', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -165.48, 'categoria': 'Transporte', 'descricao': 'Uber', 'data': '2024-06-29', 'is_fixo': False, 'status': 'pago'},
        {'id': '5017df88-3482-4114-8700-f9bdcf3be7ac', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -16.54, 'categoria': 'Lazer', 'descricao': 'Cinema', 'data': '2024-06-12', 'is_fixo': False, 'status': 'pago'},
        {'id': 'aa43ab1a-fae1-455b-860f-90236a6db90e', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -137.89, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2024-06-01', 'is_fixo': True, 'status': 'pendente'},
        {'id': '5b7190f8-b39b-4497-ae66-88def7d81232', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -141.67, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2024-05-27', 'is_fixo': True, 'status': 'pendente'},
        {'id': '2f782c5f-08f3-4e4b-b016-17b70f074465', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -105.79, 'categoria': 'Utilidades', 'descricao': 'Água', 'data': '2024-05-21', 'is_fixo': True, 'status': 'pago'},
        {'id': 'd735072c-80ed-4fb1-9024-5d5b76611394', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -181.39, 'categoria': 'Moradia', 'descricao': 'IPTU', 'data': '2024-05-20', 'is_fixo': True, 'status': 'pago'},
        {'id': '5091da58-4f19-4f1e-a4e8-8cf042113630', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -123.29, 'categoria': 'Transporte', 'descricao': 'Combustível', 'data': '2024-04-17', 'is_fixo': True, 'status': 'pago'},
        {'id': '7c2b7557-c6be-406c-817c-5aaef41dfb7d', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -156.1, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2024-04-07', 'is_fixo': True, 'status': 'pendente'},
        {'id': '30f0f3d4-6daf-428c-8e9c-7791195f1a95', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -101.17, 'categoria': 'Transporte', 'descricao': 'Metrô', 'data': '2024-04-06', 'is_fixo': True, 'status': 'pago'},
        {'id': '2ec3c6b2-75af-4ae6-9520-fad68aa1c3e9', 'wallet_id': '00000000-0000-0000-0000-000000000001', 'valor': -183.49, 'categoria': 'Alimentação', 'descricao': 'Restaurante', 'data': '2024-04-03', 'is_fixo': False, 'status': 'pendente'},
        {'id': 'c87d02b3-e6eb-434c-b60b-657c8a23370b', 'wallet_id': '00000000-0000-0000-0000-000000000002', 'valor': -121.18, 'categoria': 'Alimentação', 'descricao': 'Padaria', 'data': '2024-04-03', 'is_fixo': True, 'status': 'pago'}
    ]
}


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


def register_transaction(
    wallet_id: str, 
    valor: float, 
    categoria: str, 
    descricao: str, 
    date: str, 
    is_fixo: bool, 
    status: str,
    metodo_pagamento: str = 'dinheiro',
    total_parcelas: int = 1
) -> bool:
    """Registra uma ou mais transações (se parcelado)."""
    client = get_supabase_client()
    user = get_state("user")
    
    # Prepara a lista de transações a inserir
    transacoes_para_inserir = []
    group_id = str(uuid.uuid4()) if total_parcelas > 1 else None
    
    base_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    for i in range(total_parcelas):
        # Se for crédito parcelado, a primeira parcela começa no mês seguinte (conforme pedido do user)
        # Se for 1 parcela só ou outro método, mantém a data original
        current_date_parcela = base_date + relativedelta(months=i + (1 if total_parcelas > 1 else 0))
        
        # Ajuste de dízimas: divide o valor total pelo número de parcelas
        # Para evitar problemas de arredondamento, calculamos a parcela base 
        # e a diferença jogamos na última parcela.
        if total_parcelas > 1:
            valor_parcela = round(valor / total_parcelas, 2)
            if i == total_parcelas - 1:
                # Ajuste final para bater o valor total
                valor_total_acumulado = valor_parcela * (total_parcelas - 1)
                valor_parcela = round(valor - valor_total_acumulado, 2)
            
            desc_parcela = f"{descricao} ({i+1}/{total_parcelas})"
        else:
            valor_parcela = valor
            desc_parcela = descricao

        t_data = {
            "wallet_id": wallet_id,
            "valor": valor_parcela,
            "categoria": categoria,
            "descricao": desc_parcela,
            "data": str(current_date_parcela),
            "is_fixo": is_fixo,
            "status": status,
            "metodo_pagamento": metodo_pagamento,
            "parcela_atual": i + 1,
            "total_parcelas": total_parcelas,
            "group_id": group_id
        }
        
        if user:
            t_data["created_by"] = user.id
            
        transacoes_para_inserir.append(t_data)

    if client and user:
        try:
            client.table("transactions").insert(transacoes_para_inserir).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar transação: {e}")
            return False
            
    # Fallback pro MOCK
    for t in transacoes_para_inserir:
        t['id'] = str(uuid.uuid4())
        MOCK_DATA['transactions'].insert(0, t)
    return True

def delete_transaction(transaction_id: str, delete_all_remaining: bool = False, group_id: Optional[str] = None) -> bool:
    """Deleta uma ou todas as parcelas restantes."""
    client = get_supabase_client()
    user = get_state("user")

    if client and user:
        try:
            query = client.table("transactions").delete()
            if delete_all_remaining and group_id:
                # Deleta a atual e as futuras do mesmo grupo
                # Nota: Em uma implementação real, poderíamos filtrar por data >= atual_sessao
                # Mas para simplificar, deletamos todas do grupo.
                query = query.eq("group_id", group_id)
            else:
                query = query.eq("id", transaction_id)
            
            query.execute()
            return True
        except Exception as e:
            st.error(f"Erro ao deletar transação: {e}")
            return False

    # Fallback pro MOCK
    if delete_all_remaining and group_id:
        MOCK_DATA['transactions'] = [t for t in MOCK_DATA['transactions'] if str(t.get('group_id')) != str(group_id)]
    else:
        MOCK_DATA['transactions'] = [t for t in MOCK_DATA['transactions'] if str(t['id']) != str(transaction_id)]
    return True

def update_transaction(transaction_id: str, valor: float, categoria: str, descricao: str, date: str, is_fixo: bool, status: str) -> bool:
    """Atualiza uma transação existente."""
    client = get_supabase_client()
    user = get_state("user")

    if client and user:
        try:
            client.table("transactions").update({
                "valor": valor,
                "categoria": categoria,
                "descricao": descricao,
                "data": date,
                "is_fixo": is_fixo,
                "status": status
            }).eq("id", transaction_id).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar transação: {e}")
            return False

    # Fallback pro MOCK
    for t in MOCK_DATA['transactions']:
        if str(t['id']) == str(transaction_id):
            t.update({"valor": valor, "categoria": categoria, "descricao": descricao, "data": date, "is_fixo": is_fixo, "status": status})
    return True
