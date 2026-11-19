import importlib.util
import json
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "openwebui" / "tools"


def load_tools(module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, TOOLS_DIR / f"{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tools()


sender = load_tools("sender_kit")
content = load_tools("content_kit")
payment = load_tools("payment_kit")


def call(method, *args) -> dict:
    return json.loads(method(*args))


class ScenarioCoverage(unittest.TestCase):
    def assertFound(self, result: dict, expected_status: str = "encontrado"):
        self.assertEqual(result["status"], expected_status, result)
        self.assertIn("SIMULADO", result["ambiente"])

    def test_d1(self):
        self.assertEqual(call(sender.check_brand_similarity, "atendimento@bancoaurora-digital.com")["marca_imitada"], "Banco Aurora")
        self.assertEqual(call(sender.lookup_domain, "bancoaurora-digital.com")["idade_em_dias"], 6)
        self.assertEqual(call(sender.check_email_authentication, "Banco Aurora <atendimento@bancoaurora-digital.com>")["dmarc"], "pass")
        expanded = call(content.expand_url, "encurta.me/aUr0ra")
        self.assertEqual(expanded["dominio_do_destino_final"], "bancoaurora-digital.com")
        self.assertEqual(call(content.check_url_reputation, expanded["destino_final"])["reputacao"], "maliciosa")
        self.assertIn("bancoaurora.com.br", call(sender.get_official_channels, "Banco Aurora")["dominios_oficiais"])

    def test_m1(self):
        self.assertEqual(call(payment.check_phone, "+55 21 98833-1057")["denuncias"], 130)
        expanded = call(content.expand_url, "encurta.me/rX9a2")
        self.assertEqual(expanded["dominio_do_destino_final"], "rapidex-taxa.top")
        self.assertEqual(call(content.check_url_reputation, "rapidex-taxa.top")["reputacao"], "maliciosa")
        self.assertEqual(call(sender.check_brand_similarity, "rapidex-taxa.top")["status"], "imita_marca")

    def test_m2(self):
        self.assertEqual(call(sender.lookup_domain, "https://folhamais-portal.com.br/colaborador/informe-rendimentos")["idade_em_dias"], 4)
        self.assertEqual(call(content.check_url_reputation, "folhamais-portal.com.br")["reputacao"], "sem_registro")
        self.assertEqual(call(sender.check_brand_similarity, "folhamais-portal.com.br")["marca_imitada"], "Folha+")
        self.assertEqual(call(sender.check_email_authentication, "noreply@folhamais-portal.com.br")["spf"], "pass")
        self.assertFound(call(sender.lookup_cnpj, "40.118.392/0001-66"))

    def test_m3(self):
        self.assertEqual(call(sender.check_email_authentication, "alertas@bancoaurora.com.br")["dmarc"], "pass")
        expanded = call(content.expand_url, "aurora.link/bloq7")
        self.assertEqual(expanded["dominio_do_destino_final"], "app.bancoaurora.com.br")
        self.assertEqual(call(content.check_url_reputation, expanded["destino_final"])["reputacao"], "limpa")
        self.assertEqual(call(sender.check_brand_similarity, "aurora.link")["status"], "dominio_oficial")

    def test_m4(self):
        self.assertEqual(call(payment.decode_boleto, "98990.00125 34567.890123 45678.901234 5 10230000028743")["beneficiario"], "LUMINA ENERGIA S.A.")
        self.assertEqual(call(payment.lookup_pix_key, "08.663.120/0001-52")["titular"], "Lumina Energia S.A.")
        self.assertEqual(call(content.analyze_attachment, "fatura_lumina_nov2026.pdf")["deteccoes_antivirus"], "0 de 70")
        self.assertEqual(call(sender.check_brand_similarity, "fatura@luminaenergia.com.br")["status"], "dominio_oficial")

    def test_m5(self):
        pix = call(payment.lookup_pix_key, "e3b7c1a9-5f42-4d8e-9a61-2c0f7b8d4e15")
        self.assertEqual(pix["tipo_de_pessoa"], "Pessoa física")
        self.assertEqual(call(sender.lookup_domain, "luminaenergia-faturas.com.br")["idade_em_dias"], 12)
        self.assertEqual(call(sender.check_brand_similarity, "luminaenergia-faturas.com.br")["marca_imitada"], "Lumina Energia")
        self.assertTrue(any("CNPJ" in rule for rule in call(sender.get_official_channels, "Lumina Energia")["politica_de_comunicacao"]))

    def test_m6(self):
        auth = call(sender.check_email_authentication, "financeiro@prismacontabil.com.br", "prisma.financeiro@caixapostal-online.net")
        self.assertEqual(auth["spf"], "fail")
        self.assertTrue(auth["responder_para_e_de_outro_dominio"])
        self.assertTrue(call(content.analyze_attachment, "NFe_4587_novembro.xlsm")["macro_executa_ao_abrir"])
        self.assertEqual(call(content.check_url_reputation, "caixapostal-online.net")["reputacao"], "suspeita")

    def test_m7(self):
        self.assertEqual(call(payment.check_phone, "+55 11 97412-3388")["ativado_ha"], "3 dias")
        self.assertEqual(call(payment.lookup_pix_key, "9c0d2e71-3b5a-4f86-b7d4-61a8e5c2f903")["titular"], "Juliana P. Costa")

    def test_m8(self):
        self.assertEqual(call(content.check_url_reputation, "https://telamax-billing.com/conta/pagamento")["reputacao"], "maliciosa")
        self.assertEqual(call(sender.check_email_authentication, "conta@telamax-billing.com")["spf"], "softfail")
        self.assertEqual(call(sender.check_brand_similarity, "telamax-billing.com")["marca_imitada"], "TelaMax")

    def test_r1(self):
        phone = call(payment.check_phone, "+55 11 3003-7739")
        self.assertTrue(phone["conta_comercial_verificada"])
        self.assertEqual(call(content.expand_url, "rapidex.com.br/rastreio/BR5520")["link_encurtado"], False)
        self.assertEqual(call(content.check_url_reputation, "rapidex.com.br/rastreio/BR5520")["reputacao"], "limpa")

    def test_r2(self):
        self.assertEqual(call(sender.check_email_authentication, "financeiro@habitatgestao.com.br")["dmarc"], "pass")
        boleto = call(payment.decode_boleto, "98790.00418 52771.093011 82400.177551 3 10230000084500")
        self.assertEqual(boleto["beneficiario"], "M R LIMA SERVICOS DIGITAIS LTDA")
        self.assertEqual(call(sender.lookup_cnpj, "52.771.093/0001-24")["tempo_de_existencia"], "25 dias")
        self.assertEqual(call(content.analyze_attachment, "boleto_condominio_nov.pdf")["deteccoes_antivirus"], "0 de 70")


class RealWorldDataIsRejected(unittest.TestCase):
    def test_unknown_inputs_return_out_of_scope(self):
        cases = [
            (sender.lookup_domain, "gmail.com"),
            (sender.check_email_authentication, "alguem@gmail.com"),
            (sender.get_official_channels, "Itaú"),
            (sender.lookup_cnpj, "00.000.000/0001-91"),
            (content.expand_url, "bit.ly/3xYz"),
            (content.expand_url, "https://www.google.com"),
            (content.check_url_reputation, "google.com"),
            (content.analyze_attachment, "contrato.pdf"),
            (payment.lookup_pix_key, "fulano@gmail.com"),
            (payment.decode_boleto, "23790.12345 60000.000000 00000.000000 1 00000000010000"),
            (payment.check_phone, "+55 11 99999-0000"),
        ]
        for method, value in cases:
            with self.subTest(value=value):
                result = call(method, value)
                self.assertEqual(result["status"], "fora_da_base_simulada")
                self.assertIn("dados reais", result["orientacao"])

    def test_brand_similarity_on_unknown_domain_is_explicitly_limited(self):
        result = call(sender.check_brand_similarity, "gmail.com")
        self.assertEqual(result["status"], "sem_semelhanca")
        self.assertIn("fictícias", result["observacao"])


if __name__ == "__main__":
    unittest.main()
