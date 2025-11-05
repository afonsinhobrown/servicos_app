# reset_database.py
from database import engine, db_session
from models import Base
import os


def reset_database():
    print("🔄 RECRIANDO BANCO DE DADOS...")

    try:
        # Drop todas as tabelas
        print("🗑️  Removendo tabelas antigas...")
        Base.metadata.drop_all(bind=engine)

        # Criar tabelas com nova estrutura
        print("🏗️  Criando tabelas atualizadas...")
        Base.metadata.create_all(bind=engine)

        print("✅ Banco de dados recriado com sucesso!")
        print("📊 Estrutura atualizada com todos os novos campos:")
        print("   • taxa_plataforma, raio_atuacao, etc. em prestadores_servico")
        print("   • tags, ativo em servicos")
        print("   • Todas as novas tabelas: conversas, mensagens, pagamentos, etc.")

    except Exception as e:
        print(f"❌ Erro ao recriar banco: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    reset_database()