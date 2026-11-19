"""
title: Kit Pagamentos e Telefone
author: Workshop Agents & Skills
version: 1.0.0
description: Investiga pedidos de pagamento e números de telefone: titular de chave PIX, decodificação de boleto e reputação de telefones (SMS e WhatsApp). Base de dados SIMULADA do workshop.
"""

import json
import re
from datetime import date, timedelta

SIMULATION_NOTICE = "SIMULADO: dado da base fictícia do workshop. Não vale para mensagens reais."

OUT_OF_SCOPE_GUIDANCE = (
    "Este ambiente de treinamento contém apenas os dados fictícios das mensagens do workshop. "
    "Não é possível verificar dados reais aqui. Informe ao usuário que esta verificação não pôde "
    "ser feita e que mensagens reais devem ser analisadas pelas ferramentas e pela equipe de segurança oficiais."
)

PIX_KEYS = {
    "e3b7c1a9-5f42-4d8e-9a61-2c0f7b8d4e15": {
        "key_type": "aleatória",
        "holder": "Rafael M. Souza",
        "person_type": "Pessoa física",
        "document": "CPF ***.482.917-**",
        "institution": "NeoPay Instituição de Pagamento",
        "created_days": 6,
        "fraud_notices": 3,
    },
    "9c0d2e71-3b5a-4f86-b7d4-61a8e5c2f903": {
        "key_type": "aleatória",
        "holder": "Juliana P. Costa",
        "person_type": "Pessoa física",
        "document": "CPF ***.115.630-**",
        "institution": "Banco Vértice S.A.",
        "created_days": 2,
        "fraud_notices": 11,
    },
    "08663120000152": {
        "key_type": "CNPJ",
        "holder": "Lumina Energia S.A.",
        "person_type": "Pessoa jurídica",
        "document": "CNPJ 08.663.120/0001-52",
        "institution": "Banco Aurora S.A.",
        "created_days": 1500,
        "fraud_notices": 0,
    },
}

BOLETOS = {
    "98990001253456789012345678901234510230000028743": {
        "bank": "989 - Banco Aurora S.A.",
        "beneficiary": "LUMINA ENERGIA S.A.",
        "beneficiary_document": "CNPJ 08.663.120/0001-52",
        "amount": "R$ 287,43",
        "due_date": "10/12",
    },
    "98790004185277109301182400177551310230000084500": {
        "bank": "987 - NeoPay Instituição de Pagamento",
        "beneficiary": "M R LIMA SERVICOS DIGITAIS LTDA",
        "beneficiary_document": "CNPJ 52.771.093/0001-24",
        "amount": "R$ 845,00",
        "due_date": "05/12",
    },
}

PHONES = {
    "5521988331057": {
        "line_type": "Celular pré-pago",
        "owner": "Não identificado",
        "activated_days": 5,
        "verified_business": False,
        "reports": 130,
        "report_categories": ["SMS de cobrança falsa de taxa de entrega"],
    },
    "5511974123388": {
        "line_type": "Celular pré-pago",
        "owner": "Não identificado",
        "activated_days": 3,
        "verified_business": False,
        "reports": 47,
        "report_categories": ["Golpe do falso parente / número novo no WhatsApp"],
    },
    "551130037739": {
        "line_type": "Fixo empresarial com WhatsApp Business",
        "owner": "RapidEx Logística Ltda",
        "activated_days": 4100,
        "verified_business": True,
        "reports": 0,
        "report_categories": [],
    },
    "551140202026": {
        "line_type": "Fixo empresarial com WhatsApp Business",
        "owner": "Banco Aurora S.A.",
        "activated_days": 3300,
        "verified_business": True,
        "reports": 0,
        "report_categories": [],
    },
    "28780": {
        "line_type": "Short code de SMS corporativo",
        "owner": "Banco Aurora S.A.",
        "activated_days": 4700,
        "verified_business": True,
        "reports": 0,
        "report_categories": [],
    },
    "08007772026": {
        "line_type": "0800 (SAC)",
        "owner": "Banco Aurora S.A.",
        "activated_days": 9000,
        "verified_business": True,
        "reports": 0,
        "report_categories": [],
    },
}


def _respond(payload: dict) -> str:
    return json.dumps({"ambiente": SIMULATION_NOTICE, **payload}, ensure_ascii=False, indent=2)


def _out_of_scope(value: str) -> str:
    return _respond({"status": "fora_da_base_simulada", "consultado": value, "orientacao": OUT_OF_SCOPE_GUIDANCE})


def _date_days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).strftime("%d/%m/%Y")


def _describe_age(days: int) -> str:
    if days < 60:
        return f"{days} dias"
    if days < 730:
        return f"{days // 30} meses"
    return f"{days // 365} anos"


def _normalize_pix_key(key: str) -> str:
    text = key.strip().strip("\"'").lower()
    if re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text):
        return text
    if "@" in text:
        return text
    return re.sub(r"\D", "", text)


def _normalize_phone(number: str) -> str:
    digits = re.sub(r"\D", "", number)
    if digits.startswith("0800"):
        return digits
    if len(digits) in (10, 11):
        return "55" + digits
    return digits


class Tools:
    def __init__(self):
        pass

    def lookup_pix_key(self, pix_key: str) -> str:
        """
        Show who receives money sent to a PIX key (the same data a banking app shows on the PIX confirmation screen), plus fraud notices.
        Use it to compare the key holder with the company or person the message claims to be.
        :param pix_key: The PIX key exactly as it appears in the message (random key, CPF, CNPJ, e-mail or phone).
        :return: JSON with the key holder, person type, institution, key age and fraud notices.
        """
        data = PIX_KEYS.get(_normalize_pix_key(pix_key))
        if not data:
            return _out_of_scope(pix_key)
        return _respond(
            {
                "status": "encontrado",
                "chave": pix_key.strip(),
                "tipo_de_chave": data["key_type"],
                "titular": data["holder"],
                "tipo_de_pessoa": data["person_type"],
                "documento": data["document"],
                "instituicao": data["institution"],
                "chave_cadastrada_em": _date_days_ago(data["created_days"]),
                "idade_da_chave": _describe_age(data["created_days"]),
                "notificacoes_de_fraude": data["fraud_notices"],
            }
        )

    def decode_boleto(self, digitable_line: str) -> str:
        """
        Decode a Brazilian boleto digitable line ("linha digitável") and show the issuing bank, the real beneficiary, amount and due date.
        Use it to check whether the money goes to the company the message claims to be.
        :param digitable_line: The boleto digitable line, with or without dots and spaces.
        :return: JSON with the issuing bank, beneficiary and amount.
        """
        data = BOLETOS.get(re.sub(r"\D", "", digitable_line))
        if not data:
            return _out_of_scope(digitable_line)
        return _respond(
            {
                "status": "encontrado",
                "banco_emissor": data["bank"],
                "beneficiario": data["beneficiary"],
                "documento_do_beneficiario": data["beneficiary_document"],
                "valor": data["amount"],
                "vencimento": data["due_date"],
            }
        )

    def check_phone(self, phone_number: str) -> str:
        """
        Check a phone number or SMS short code: line type, owner, activation age, verified business account and abuse reports.
        Use it for SMS and WhatsApp messages.
        :param phone_number: The number exactly as shown in the message, e.g. "+55 11 91234-5678" or "28780".
        :return: JSON with the phone number facts.
        """
        data = PHONES.get(_normalize_phone(phone_number))
        if not data:
            return _out_of_scope(phone_number)
        return _respond(
            {
                "status": "encontrado",
                "numero": phone_number.strip(),
                "tipo_de_linha": data["line_type"],
                "titular": data["owner"],
                "ativado_ha": _describe_age(data["activated_days"]),
                "conta_comercial_verificada": data["verified_business"],
                "denuncias": data["reports"],
                "categorias_das_denuncias": data["report_categories"],
            }
        )
