import os
import sqlite3
import sys


def fazer_dump(banco_entrada, arquivo_saida):
    """Faz dump completo do banco SQLite"""
    try:
        # Conectar ao banco
        conn = sqlite3.connect(banco_entrada)

        # Criar arquivo de dump
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            # Escrever todas as linhas do dump
            for linha in conn.iterdump():
                f.write(f"{linha};\n")

        conn.close()
        print(f"✅ Dump criado com sucesso: {arquivo_saida}")
        print(f"📊 Tamanho do arquivo: {os.path.getsize(arquivo_saida)} bytes")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        fazer_dump(sys.argv[1], sys.argv[2])
    else:
        # Uso padrão
        fazer_dump('servicos_app.db', 'servicos_app.sql')