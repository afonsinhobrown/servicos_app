import sqlite3
import os
import sys


def restaurar_dump(arquivo_dump, banco_saida='servicos_app.db'):
    """Restaura um dump SQLite para um novo banco"""

    # Remover banco existente se existir
    if os.path.exists(banco_saida):
        os.remove(banco_saida)
        print(f"🗑️  Banco antigo removido: {banco_saida}")

    try:
        # Criar novo banco
        conn = sqlite3.connect(banco_saida)
        cursor = conn.cursor()

        # Ler e executar o dump
        with open(arquivo_dump, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Executar todo o script SQL
        cursor.executescript(sql_script)

        conn.commit()
        conn.close()

        print(f"✅ Backup restaurado com sucesso: {banco_saida}")
        print(f"📊 Tamanho do novo banco: {os.path.getsize(banco_saida)} bytes")

    except Exception as e:
        print(f"❌ Erro ao restaurar: {e}")
        # Se der erro, remove o banco incompleto
        if os.path.exists(banco_saida):
            os.remove(banco_saida)


# Uso
if __name__ == "__main__":
    arquivo_dump = 'servicos_app.sql'  # Altere para o nome do seu dump
    restaurar_dump(arquivo_dump)