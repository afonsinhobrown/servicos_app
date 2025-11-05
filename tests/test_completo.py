# tests/test_completo.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"


class TestServicosPro:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, success, message=""):
        status = "✅ PASSOU" if success else "❌ FALHOU"
        result = f"{status} | {test_name}"
        if message:
            result += f" | {message}"
        self.test_results.append(result)
        print(result)

    def test_fluxo_completo(self):
        """Testar fluxo completo"""
        print("\n" + "=" * 60)
        print("🧪 INICIANDO TESTES COMPLETOS - SERVIÇOSPRO")
        print("=" * 60)

        # Testar APIs básicas primeiro
        self.test_apis_basicas()

        # Testar páginas
        self.test_paginas()

        self.relatorio_final()

    def test_apis_basicas(self):
        """Testar APIs básicas"""
        print("\n📡 TESTANDO APIS:")

        apis = [
            ("/api/prestadores", "GET"),
            ("/api/servicos", "GET"),
            ("/api/categorias", "GET"),
            ("/api/estatisticas", "GET"),
            ("/avaliacoes/api/estatisticas/1", "GET"),
            ("/chat/api/conversas", "GET"),
            ("/pagamentos/api/transacoes", "GET")
        ]

        for api, method in apis:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{api}")
                else:
                    response = self.session.post(f"{BASE_URL}{api}")

                success = response.status_code == 200
                detalhes = f"Status: {response.status_code}"

                if response.status_code == 500:
                    try:
                        erro = response.json().get('error', 'Erro desconhecido')
                        detalhes += f" | Erro: {erro}"
                    except:
                        detalhes += " | Erro interno"
                elif response.status_code == 400:
                    detalhes += " | Bad Request"

                self.log_test(f"API {api}", success, detalhes)

            except Exception as e:
                self.log_test(f"API {api}", False, f"Exception: {str(e)}")

    def test_paginas(self):
        """Testar páginas principais"""
        print("\n🌐 TESTANDO PÁGINAS:")

        paginas = [
            "/",
            "/servicos/buscar",
            "/sobre",
            "/contato",
            "/auth/login",
            "/auth/registro"
        ]

        for pagina in paginas:
            try:
                response = self.session.get(f"{BASE_URL}{pagina}")
                success = response.status_code == 200
                self.log_test(f"Página {pagina}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Página {pagina}", False, f"Erro: {str(e)}")

    def relatorio_final(self):
        """Gerar relatório final"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DE TESTES")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if "✅" in r)
        failed_tests = total_tests - passed_tests

        for result in self.test_results:
            print(result)

        print("\n" + "=" * 60)
        print(f"TOTAL: {total_tests} testes | ✅ {passed_tests} | ❌ {failed_tests}")
        print("=" * 60)

        if failed_tests == 0:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para deploy.")
        else:
            print(f"⚠️  {failed_tests} teste(s) falharam.")

            # Recomendações baseadas nos erros
            erros_500 = sum(1 for r in self.test_results if "Status: 500" in r)
            erros_400 = sum(1 for r in self.test_results if "Status: 400" in r)

            if erros_500 > 0:
                print("\n💡 RECOMENDAÇÃO: Execute 'python tests/criar_dados_teste.py' para criar dados iniciais")
            if erros_400 > 0:
                print("💡 RECOMENDAÇÃO: Verifique parâmetros das APIs")


if __name__ == "__main__":
    tester = TestServicosPro()
    tester.test_fluxo_completo()