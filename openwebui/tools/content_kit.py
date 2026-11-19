"""
title: Kit Conteúdo
author: Workshop Agents & Skills
version: 1.0.0
description: Investiga o que vem dentro da mensagem: para onde levam os links encurtados, reputação de links e domínios, e análise de anexos. Base de dados SIMULADA do workshop.
"""

import json
import re

SIMULATION_NOTICE = "SIMULADO: dado da base fictícia do workshop. Não vale para mensagens reais."

OUT_OF_SCOPE_GUIDANCE = (
    "Este ambiente de treinamento contém apenas os dados fictícios das mensagens do workshop. "
    "Não é possível verificar dados reais aqui. Informe ao usuário que esta verificação não pôde "
    "ser feita e que mensagens reais devem ser analisadas pelas ferramentas e pela equipe de segurança oficiais."
)

URL_SHORTENERS = {"encurta.me", "aurora.link", "bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "t.co", "encurtador.com.br", "rebrand.ly"}

SHORT_LINKS = {
    "encurta.me/aur0ra": [
        {"url": "https://encurta.me/aUr0ra", "redireciona_com": "HTTP 301"},
        {"url": "http://bancoaurora-digital.com/r?c=88", "redireciona_com": "HTTP 302"},
        {"url": "https://bancoaurora-digital.com/login/atualizacao-cadastral", "redireciona_com": "destino final"},
    ],
    "encurta.me/rx9a2": [
        {"url": "https://encurta.me/rX9a2", "redireciona_com": "HTTP 301"},
        {"url": "https://rapidex-taxa.top/pagamento?obj=BR8812", "redireciona_com": "destino final"},
    ],
    "aurora.link/bloq7": [
        {"url": "https://aurora.link/bloq7", "redireciona_com": "HTTP 301"},
        {"url": "https://app.bancoaurora.com.br/cartoes/bloqueio", "redireciona_com": "destino final"},
    ],
}

REPUTATION = {
    "bancoaurora.com.br": {"rating": "limpa", "category": "Site oficial de instituição financeira", "reports": 0, "first_report_days": None},
    "aurora.link": {"rating": "limpa", "category": "Encurtador de links próprio do Banco Aurora", "reports": 0, "first_report_days": None},
    "rapidex.com.br": {"rating": "limpa", "category": "Site oficial de transportadora", "reports": 0, "first_report_days": None},
    "luminaenergia.com.br": {"rating": "limpa", "category": "Site oficial de concessionária de energia", "reports": 0, "first_report_days": None},
    "folhamais.com.br": {"rating": "limpa", "category": "Site oficial de software de RH", "reports": 0, "first_report_days": None},
    "telamax.com.br": {"rating": "limpa", "category": "Site oficial de streaming", "reports": 0, "first_report_days": None},
    "prismacontabil.com.br": {"rating": "limpa", "category": "Site de escritório de contabilidade", "reports": 0, "first_report_days": None},
    "habitatgestao.com.br": {"rating": "limpa", "category": "Site de administradora de condomínios", "reports": 0, "first_report_days": None},
    "encurta.me": {"rating": "neutra", "category": "Encurtador público, usado tanto por empresas legítimas quanto por golpistas. Avalie o destino final.", "reports": 0, "first_report_days": None},
    "bancoaurora-digital.com": {"rating": "maliciosa", "category": "Phishing: página falsa de login bancário", "reports": 37, "first_report_days": 3},
    "rapidex-taxa.top": {"rating": "maliciosa", "category": "Phishing: cobrança falsa de taxa de entrega", "reports": 212, "first_report_days": 2},
    "folhamais-portal.com.br": {"rating": "sem_registro", "category": "Nenhuma lista de bloqueio contém este domínio até o momento", "reports": 0, "first_report_days": None},
    "luminaenergia-faturas.com.br": {"rating": "suspeita", "category": "Possível fraude de cobrança", "reports": 4, "first_report_days": 5},
    "caixapostal-online.net": {"rating": "suspeita", "category": "Serviço de e-mail usado em campanhas de spam", "reports": 9, "first_report_days": 14},
    "telamax-billing.com": {"rating": "maliciosa", "category": "Phishing: roubo de dados de cartão", "reports": 58, "first_report_days": 6},
    "cdn-update-sync.net": {"rating": "maliciosa", "category": "Distribuição de malware", "reports": 344, "first_report_days": 40},
}

ATTACHMENTS = {
    "nfe_4587_novembro.xlsm": {
        "tipo_declarado": "Planilha do Excel (.xlsm)",
        "tipo_real": "Planilha do Excel com macros VBA",
        "contem_macros": True,
        "macro_executa_ao_abrir": True,
        "comportamento_observado": "Ao clicar em 'Habilitar Conteúdo', a macro baixa e executa um programa do endereço cdn-update-sync.net.",
        "deteccoes_antivirus": "41 de 70",
        "classificacao_dos_antivirus": "Trojan bancário (rouba senhas de internet banking)",
        "assinatura_digital": "ausente",
    },
    "fatura_lumina_nov2026.pdf": {
        "tipo_declarado": "Documento PDF",
        "tipo_real": "Documento PDF",
        "contem_macros": False,
        "contem_scripts": False,
        "links_no_documento": ["luminaenergia.com.br"],
        "deteccoes_antivirus": "0 de 70",
        "assinatura_digital": "válida, emitida para Lumina Energia S.A.",
    },
    "boleto_condominio_nov.pdf": {
        "tipo_declarado": "Documento PDF",
        "tipo_real": "Documento PDF",
        "contem_macros": False,
        "contem_scripts": False,
        "deteccoes_antivirus": "0 de 70",
        "assinatura_digital": "ausente",
        "metadados": "Arquivo criado há 2 dias com um editor de PDF online gratuito.",
        "texto_extraido_relevante": "Beneficiário: M R LIMA SERVICOS DIGITAIS LTDA",
    },
}


def _respond(payload: dict) -> str:
    return json.dumps({"ambiente": SIMULATION_NOTICE, **payload}, ensure_ascii=False, indent=2)


def _out_of_scope(value: str) -> str:
    return _respond({"status": "fora_da_base_simulada", "consultado": value, "orientacao": OUT_OF_SCOPE_GUIDANCE})


def _strip_scheme(url: str) -> str:
    text = url.strip().strip("<>\"'").lower()
    text = re.sub(r"^[a-z]+://", "", text)
    return text.removeprefix("www.")


def _extract_domain(value: str) -> str:
    text = value.strip().lower()
    email = re.search(r"[\w.+-]+@([\w-]+(\.[\w-]+)+)", text)
    if email:
        return email.group(1)
    return re.split(r"[/?#:\s]", _strip_scheme(text), maxsplit=1)[0].strip(".")


def _registered_domain(domain: str) -> str:
    for known in REPUTATION:
        if domain == known or domain.endswith("." + known):
            return known
    return domain


class Tools:
    def __init__(self):
        pass

    def expand_url(self, url: str) -> str:
        """
        Follow a (possibly shortened) link without opening it in a browser and return every redirect up to the final destination.
        Use it whenever the message has a shortened link, to discover where it really leads.
        :param url: The link exactly as it appears in the message, e.g. "encurta.me/abc123".
        :return: JSON with the redirect chain and the final destination domain.
        """
        stripped = _strip_scheme(url).rstrip("/")
        domain = _extract_domain(url)
        chain = SHORT_LINKS.get(stripped)
        if chain:
            final_url = chain[-1]["url"]
            return _respond(
                {
                    "status": "encontrado",
                    "link_encurtado": True,
                    "cadeia_de_redirecionamentos": chain,
                    "destino_final": final_url,
                    "dominio_do_destino_final": _extract_domain(final_url),
                }
            )
        if domain in URL_SHORTENERS:
            return _out_of_scope(url)
        if _registered_domain(domain) in REPUTATION:
            return _respond(
                {
                    "status": "encontrado",
                    "link_encurtado": False,
                    "destino_final": url,
                    "dominio_do_destino_final": domain,
                    "observacao": "Não é um link encurtado; o destino é o próprio endereço.",
                }
            )
        return _out_of_scope(url)

    def check_url_reputation(self, url: str) -> str:
        """
        Check a link or domain against security blocklists and abuse reports.
        Note that a brand-new malicious domain may not have been reported yet.
        :param url: A full link or just the domain.
        :return: JSON with the reputation rating, category and number of abuse reports.
        """
        domain = _registered_domain(_extract_domain(url))
        data = REPUTATION.get(domain)
        if not data:
            return _out_of_scope(url)
        result = {
            "status": "encontrado",
            "dominio": domain,
            "reputacao": data["rating"],
            "categoria": data["category"],
            "denuncias": data["reports"],
        }
        if data["first_report_days"] is not None:
            result["primeira_denuncia"] = f"há {data['first_report_days']} dias"
        return _respond(result)

    def analyze_attachment(self, filename: str) -> str:
        """
        Analyze an attachment in a sandbox: real file type, macros, scripts, observed behavior and antivirus detections.
        :param filename: The attachment file name exactly as listed in the message, e.g. "invoice.pdf".
        :return: JSON with the sandbox analysis facts.
        """
        key = filename.strip().strip("\"'").lower()
        data = ATTACHMENTS.get(key)
        if not data:
            return _out_of_scope(filename)
        return _respond({"status": "encontrado", "arquivo": filename.strip(), **data})
