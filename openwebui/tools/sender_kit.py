"""
title: Kit Remetente
author: Workshop Agents & Skills
version: 1.0.0
description: Investiga quem enviou a mensagem: idade e dono do domínio, autenticação do e-mail, imitação de marcas, canais oficiais da empresa e situação do CNPJ. Base de dados SIMULADA do workshop.
"""

import json
import re
import unicodedata
from datetime import date, timedelta

SIMULATION_NOTICE = "SIMULADO: dado da base fictícia do workshop. Não vale para mensagens reais."

OUT_OF_SCOPE_GUIDANCE = (
    "Este ambiente de treinamento contém apenas os dados fictícios das mensagens do workshop. "
    "Não é possível verificar dados reais aqui. Informe ao usuário que esta verificação não pôde "
    "ser feita e que mensagens reais devem ser analisadas pelas ferramentas e pela equipe de segurança oficiais."
)

AUTHENTICATION_EXPLANATION = (
    "SPF, DKIM e DMARC confirmam apenas se o e-mail saiu de fato de um servidor autorizado pelo domínio "
    "que aparece no remetente. Eles não dizem se esse domínio é legítimo nem se a conta foi invadida."
)

DOMAINS = {
    "bancoaurora.com.br": {"days": 10220, "registrar": "Registro.br", "registrant": "Banco Aurora S.A. (CNPJ 31.872.405/0001-17)", "country": "Brasil", "privacy": False, "mail": True},
    "aurora.link": {"days": 4380, "registrar": "GlobalNomes Registrar", "registrant": "Banco Aurora S.A.", "country": "Brasil", "privacy": False, "mail": False},
    "rapidex.com.br": {"days": 6200, "registrar": "Registro.br", "registrant": "RapidEx Logística Ltda (CNPJ 22.519.744/0001-03)", "country": "Brasil", "privacy": False, "mail": True},
    "luminaenergia.com.br": {"days": 9130, "registrar": "Registro.br", "registrant": "Lumina Energia S.A. (CNPJ 08.663.120/0001-52)", "country": "Brasil", "privacy": False, "mail": True},
    "folhamais.com.br": {"days": 3650, "registrar": "Registro.br", "registrant": "Folha+ Tecnologia em RH Ltda (CNPJ 40.118.392/0001-66)", "country": "Brasil", "privacy": False, "mail": True},
    "telamax.com.br": {"days": 2560, "registrar": "Registro.br", "registrant": "TelaMax Streaming Ltda (CNPJ 35.902.661/0001-48)", "country": "Brasil", "privacy": False, "mail": True},
    "prismacontabil.com.br": {"days": 5110, "registrar": "Registro.br", "registrant": "Prisma Contabilidade Ltda (CNPJ 19.284.507/0001-31)", "country": "Brasil", "privacy": False, "mail": True},
    "habitatgestao.com.br": {"days": 4020, "registrar": "Registro.br", "registrant": "Habitat Gestão Condominial Ltda (CNPJ 27.640.915/0001-08)", "country": "Brasil", "privacy": False, "mail": True},
    "encurta.me": {"days": 3290, "registrar": "GlobalNomes Registrar", "registrant": "Encurta.me Serviços Digitais", "country": "Portugal", "privacy": False, "mail": False},
    "bancoaurora-digital.com": {"days": 6, "registrar": "CheapDomains Registrar Ltd.", "registrant": "Oculto por serviço de privacidade", "country": "Seychelles", "privacy": True, "mail": True},
    "rapidex-taxa.top": {"days": 2, "registrar": "CheapDomains Registrar Ltd.", "registrant": "Oculto por serviço de privacidade", "country": "Desconhecido", "privacy": True, "mail": False},
    "folhamais-portal.com.br": {"days": 4, "registrar": "Registro.br", "registrant": "Pessoa física (CPF oculto)", "country": "Brasil", "privacy": True, "mail": True},
    "luminaenergia-faturas.com.br": {"days": 12, "registrar": "Registro.br", "registrant": "Pessoa física (CPF oculto)", "country": "Brasil", "privacy": True, "mail": True},
    "caixapostal-online.net": {"days": 20, "registrar": "CheapDomains Registrar Ltd.", "registrant": "Oculto por serviço de privacidade", "country": "Panamá", "privacy": True, "mail": True},
    "telamax-billing.com": {"days": 9, "registrar": "CheapDomains Registrar Ltd.", "registrant": "Oculto por serviço de privacidade", "country": "Desconhecido", "privacy": True, "mail": True},
}

EMAIL_AUTHENTICATION = {
    "atendimento@bancoaurora-digital.com": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "server": "Servidor autorizado pelo domínio bancoaurora-digital.com"},
    "noreply@folhamais-portal.com.br": {"spf": "pass", "dkim": "pass", "dmarc": "ausente", "server": "Servidor autorizado pelo domínio folhamais-portal.com.br"},
    "alertas@bancoaurora.com.br": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "server": "Servidor oficial de e-mail do Banco Aurora"},
    "fatura@luminaenergia.com.br": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "server": "Servidor oficial de e-mail da Lumina Energia"},
    "cobranca@luminaenergia-faturas.com.br": {"spf": "pass", "dkim": "ausente", "dmarc": "ausente", "server": "Servidor autorizado pelo domínio luminaenergia-faturas.com.br"},
    "financeiro@prismacontabil.com.br": {"spf": "fail", "dkim": "fail", "dmarc": "fail", "server": "IP 203.0.113.77, NÃO autorizado pelo domínio prismacontabil.com.br"},
    "conta@telamax-billing.com": {"spf": "softfail", "dkim": "ausente", "dmarc": "ausente", "server": "IP 198.51.100.23, não listado pelo domínio telamax-billing.com"},
    "financeiro@habitatgestao.com.br": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "server": "Servidor oficial de e-mail da Habitat Gestão"},
}

COMPANIES = {
    "banco_aurora": {
        "aliases": ["banco aurora", "aurora"],
        "name": "Banco Aurora S.A.",
        "official_domains": ["bancoaurora.com.br", "aurora.link"],
        "official_senders": ["alertas@bancoaurora.com.br", "comunicados@bancoaurora.com.br"],
        "phones": {"SAC": "0800 777 2026", "WhatsApp oficial": "+55 11 4020-2026", "SMS (short code)": "28780"},
        "policy": [
            "Usa o encurtador próprio aurora.link; não usa encurtadores públicos.",
            "Nunca pede senha, token ou código de segurança.",
            "Nunca pede atualização cadastral por link em e-mail ou SMS; atualização só no app.",
            "Nunca pede transferência ou PIX por mensagem.",
        ],
    },
    "rapidex": {
        "aliases": ["rapidex", "rapid ex"],
        "name": "RapidEx Logística Ltda",
        "official_domains": ["rapidex.com.br"],
        "official_senders": ["avisos@rapidex.com.br"],
        "phones": {"WhatsApp oficial (conta comercial verificada)": "+55 11 3003-7739"},
        "policy": [
            "Nunca cobra taxa de entrega, reentrega ou alfândega por SMS ou WhatsApp.",
            "Rastreamento apenas em rapidex.com.br/rastreio.",
        ],
    },
    "lumina": {
        "aliases": ["lumina energia", "lumina"],
        "name": "Lumina Energia S.A.",
        "official_domains": ["luminaenergia.com.br"],
        "official_senders": ["fatura@luminaenergia.com.br"],
        "phones": {"Central de atendimento": "0800 600 1199"},
        "policy": [
            "PIX aceito somente na chave CNPJ 08.663.120/0001-52 (titular Lumina Energia S.A.).",
            "Não usa chave PIX aleatória, de e-mail ou de pessoa física.",
            "Aviso de corte é enviado por carta com no mínimo 15 dias de antecedência; não oferece desconto para pagamento imediato.",
        ],
    },
    "folhamais": {
        "aliases": ["folha+", "folha mais", "folhamais"],
        "name": "Folha+ Tecnologia em RH Ltda",
        "official_domains": ["folhamais.com.br"],
        "official_senders": ["noreply@folhamais.com.br"],
        "phones": {"Suporte": "0800 555 0316"},
        "policy": [
            "Documentos ficam somente no portal oficial portal.folhamais.com.br.",
            "O login é feito pelo SSO da empresa cliente; a Folha+ não pede senha da rede corporativa em outros sites.",
        ],
    },
    "telamax": {
        "aliases": ["telamax", "tela max"],
        "name": "TelaMax Streaming Ltda",
        "official_domains": ["telamax.com.br"],
        "official_senders": ["conta@telamax.com.br"],
        "phones": {},
        "policy": [
            "Dados de pagamento são atualizados somente no app ou em telamax.com.br/conta.",
            "Não envia links de pagamento de domínios diferentes de telamax.com.br.",
        ],
    },
    "prisma": {
        "aliases": ["prisma contabilidade", "prisma contabil", "prisma"],
        "name": "Prisma Contabilidade Ltda",
        "official_domains": ["prismacontabil.com.br"],
        "official_senders": ["financeiro@prismacontabil.com.br"],
        "phones": {"Escritório": "+55 11 3456-7820"},
        "policy": ["Envia notas fiscais somente em PDF e XML. Nunca envia planilhas ou arquivos com macros."],
    },
    "habitat": {
        "aliases": ["habitat gestao condominial", "habitat gestao", "habitat"],
        "name": "Habitat Gestão Condominial Ltda",
        "official_domains": ["habitatgestao.com.br"],
        "official_senders": ["financeiro@habitatgestao.com.br"],
        "phones": {"Financeiro": "+55 11 3789-4400"},
        "policy": [
            "Boletos são emitidos pelo Banco Aurora (código 989) e o beneficiário é sempre Habitat Gestão Condominial Ltda.",
            "Não houve troca de banco de cobrança.",
        ],
    },
}

CNPJ_REGISTRY = {
    "31872405000117": {"aliases": ["banco aurora"], "legal_name": "BANCO AURORA S.A.", "trade_name": "Banco Aurora", "status": "Ativa", "days": 10250, "size": "Demais", "activity": "Bancos múltiplos, com carteira comercial", "city": "São Paulo/SP"},
    "22519744000103": {"aliases": ["rapidex"], "legal_name": "RAPIDEX LOGISTICA LTDA", "trade_name": "RapidEx", "status": "Ativa", "days": 6230, "size": "Demais", "activity": "Serviços de entrega rápida", "city": "Barueri/SP"},
    "08663120000152": {"aliases": ["lumina energia", "lumina"], "legal_name": "LUMINA ENERGIA S.A.", "trade_name": "Lumina Energia", "status": "Ativa", "days": 9150, "size": "Demais", "activity": "Distribuição de energia elétrica", "city": "Campinas/SP"},
    "40118392000166": {"aliases": ["folha+", "folha mais", "folhamais"], "legal_name": "FOLHA MAIS TECNOLOGIA EM RH LTDA", "trade_name": "Folha+", "status": "Ativa", "days": 3700, "size": "Empresa de pequeno porte", "activity": "Desenvolvimento de software sob encomenda", "city": "Curitiba/PR"},
    "35902661000148": {"aliases": ["telamax", "tela max"], "legal_name": "TELAMAX STREAMING LTDA", "trade_name": "TelaMax", "status": "Ativa", "days": 2600, "size": "Demais", "activity": "Distribuição de conteúdo audiovisual pela internet", "city": "Rio de Janeiro/RJ"},
    "19284507000131": {"aliases": ["prisma contabilidade", "prisma contabil", "prisma"], "legal_name": "PRISMA CONTABILIDADE LTDA", "trade_name": "Prisma Contabilidade", "status": "Ativa", "days": 5140, "size": "Microempresa", "activity": "Atividades de contabilidade", "city": "São Paulo/SP"},
    "27640915000108": {"aliases": ["habitat gestao condominial", "habitat gestao", "habitat"], "legal_name": "HABITAT GESTAO CONDOMINIAL LTDA", "trade_name": "Habitat Gestão", "status": "Ativa", "days": 4050, "size": "Empresa de pequeno porte", "activity": "Administração de condomínios prediais", "city": "São Paulo/SP"},
    "52771093000124": {"aliases": ["m r lima", "m r lima servicos digitais"], "legal_name": "M R LIMA SERVICOS DIGITAIS LTDA", "trade_name": "(sem nome fantasia)", "status": "Ativa", "days": 25, "size": "Microempresa", "activity": "Promoção de vendas", "city": "Osasco/SP"},
}

BRAND_KEYWORDS = {
    "Banco Aurora": ["bancoaurora", "aurora"],
    "RapidEx": ["rapidex"],
    "Lumina Energia": ["luminaenergia", "lumina"],
    "Folha+": ["folhamais"],
    "TelaMax": ["telamax"],
    "Prisma Contabilidade": ["prismacontabil"],
    "Habitat Gestão": ["habitatgestao"],
}

TLD_SUFFIXES = (".com.br", ".net.br", ".org.br", ".com", ".net", ".org", ".top", ".me", ".link", ".br", ".online", ".site")


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


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", _strip_accents(text).lower().replace("-", " ")).strip()


def _extract_email(value: str) -> str:
    match = re.search(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", value.lower())
    return match.group(0) if match else ""


def _extract_domain(value: str) -> str:
    text = value.strip().lower()
    email = _extract_email(text)
    if email:
        return email.split("@", 1)[1]
    text = re.sub(r"^[a-z]+://", "", text)
    text = re.split(r"[/?#:\s]", text, maxsplit=1)[0]
    return text.removeprefix("www.").strip(".")


def _registered_domain(domain: str) -> str:
    for known in DOMAINS:
        if domain == known or domain.endswith("." + known):
            return known
    return domain


def _label_without_tld(domain: str) -> str:
    for suffix in TLD_SUFFIXES:
        if domain.endswith(suffix):
            domain = domain[: -len(suffix)]
            break
    return domain.split(".")[-1]


def _edit_distance(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (char_a != char_b)))
        previous = current
    return previous[-1]


def _find_company(query: str):
    normalized = _normalize_text(query)
    domain = _registered_domain(_extract_domain(query))
    for company in COMPANIES.values():
        if domain in company["official_domains"]:
            return company
    for company in COMPANIES.values():
        if any(alias in normalized for alias in company["aliases"]):
            return company
    return None


class Tools:
    def __init__(self):
        pass

    def lookup_domain(self, domain: str) -> str:
        """
        Look up WHOIS registration data for a domain: creation date, age, registrar, owner and country.
        Use it to find out whether the sender's or a link's domain was created recently or hides its owner.
        :param domain: A domain, e-mail address or URL, e.g. "example.com.br" or "someone@example.com.br".
        :return: JSON with the domain registration facts.
        """
        registered = _registered_domain(_extract_domain(domain))
        data = DOMAINS.get(registered)
        if not data:
            return _out_of_scope(domain)
        return _respond(
            {
                "status": "encontrado",
                "dominio": registered,
                "data_de_criacao": _date_days_ago(data["days"]),
                "idade": _describe_age(data["days"]),
                "idade_em_dias": data["days"],
                "registrador": data["registrar"],
                "titular": data["registrant"],
                "pais_do_titular": data["country"],
                "titular_oculto": data["privacy"],
                "possui_servidor_de_email": data["mail"],
            }
        )

    def check_email_authentication(self, sender: str, reply_to: str = "") -> str:
        """
        Check SPF, DKIM and DMARC results for the sender address, and whether the Reply-To address differs from the sender.
        Use it to find out whether the "From" address was forged.
        :param sender: The sender e-mail address exactly as it appears in the "De"/"From" field.
        :param reply_to: Optional. The "Responder para"/"Reply-To" address, if the message has one.
        :return: JSON with the authentication results and Reply-To comparison.
        """
        address = _extract_email(sender)
        data = EMAIL_AUTHENTICATION.get(address)
        if not data:
            return _out_of_scope(sender)
        result = {
            "status": "encontrado",
            "remetente": address,
            "spf": data["spf"],
            "dkim": data["dkim"],
            "dmarc": data["dmarc"],
            "servidor_que_enviou": data["server"],
            "o_que_significa": AUTHENTICATION_EXPLANATION,
        }
        reply_address = _extract_email(reply_to) if reply_to else ""
        if reply_address:
            result["responder_para"] = reply_address
            result["responder_para_e_de_outro_dominio"] = reply_address.split("@")[1] != address.split("@")[1]
        return _respond(result)

    def check_brand_similarity(self, domain: str) -> str:
        """
        Compare a domain with the official domains of known brands to detect imitation (typosquatting, brand name plus extra words).
        :param domain: A domain, e-mail address or URL to compare.
        :return: JSON saying whether the domain is official, imitates a brand, or has no similarity.
        """
        target = _extract_domain(domain)
        if not target:
            return _out_of_scope(domain)
        for company in COMPANIES.values():
            for official in company["official_domains"]:
                if target == official or target.endswith("." + official):
                    return _respond({"status": "dominio_oficial", "dominio": target, "marca": company["name"]})
        label = _label_without_tld(_registered_domain(target))
        compact = label.replace("-", "")
        for brand, keywords in BRAND_KEYWORDS.items():
            for keyword in keywords:
                if keyword in compact:
                    return _respond(
                        {
                            "status": "imita_marca",
                            "dominio": target,
                            "marca_imitada": brand,
                            "tecnica": f"usa o nome da marca ('{keyword}') combinado com outras palavras em um domínio que não é o oficial",
                            "dominios_oficiais_da_marca": _find_company(brand)["official_domains"],
                        }
                    )
                if len(keyword) >= 6 and _edit_distance(compact, keyword) <= 2:
                    return _respond(
                        {
                            "status": "imita_marca",
                            "dominio": target,
                            "marca_imitada": brand,
                            "tecnica": "grafia muito parecida com o nome da marca (troca, falta ou sobra de letras)",
                            "dominios_oficiais_da_marca": _find_company(brand)["official_domains"],
                        }
                    )
        return _respond(
            {
                "status": "sem_semelhanca",
                "dominio": target,
                "observacao": "Comparação feita apenas com as marcas fictícias cadastradas no cenário do workshop.",
            }
        )

    def get_official_channels(self, company: str) -> str:
        """
        Get the official communication channels of a company (domains, sender addresses, phone numbers) and what it never asks customers by message.
        Use it to compare what the message claims with how the real company communicates.
        :param company: Company name or one of its domains, e.g. "Banco Aurora" or "bancoaurora.com.br".
        :return: JSON with official domains, senders, phones and communication policy.
        """
        found = _find_company(company)
        if not found:
            return _out_of_scope(company)
        return _respond(
            {
                "status": "encontrado",
                "empresa": found["name"],
                "dominios_oficiais": found["official_domains"],
                "remetentes_oficiais": found["official_senders"],
                "telefones_oficiais": found["phones"],
                "politica_de_comunicacao": found["policy"],
            }
        )

    def lookup_cnpj(self, query: str) -> str:
        """
        Look up a Brazilian company registration (CNPJ): legal name, status, opening date, size and main activity.
        :param query: A CNPJ (with or without punctuation) or a company name.
        :return: JSON with the company registration facts.
        """
        digits = re.sub(r"\D", "", query)
        record = CNPJ_REGISTRY.get(digits) if len(digits) == 14 else None
        if not record:
            normalized = _normalize_text(query)
            for cnpj, candidate in CNPJ_REGISTRY.items():
                if any(alias in normalized for alias in candidate["aliases"]):
                    digits, record = cnpj, candidate
                    break
        if not record:
            return _out_of_scope(query)
        formatted = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        return _respond(
            {
                "status": "encontrado",
                "cnpj": formatted,
                "razao_social": record["legal_name"],
                "nome_fantasia": record["trade_name"],
                "situacao_cadastral": record["status"],
                "data_de_abertura": _date_days_ago(record["days"]),
                "tempo_de_existencia": _describe_age(record["days"]),
                "porte": record["size"],
                "atividade_principal": record["activity"],
                "municipio": record["city"],
            }
        )
