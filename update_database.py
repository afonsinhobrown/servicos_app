# update_database.py
from database import engine, db_session
from models import Base
from sqlalchemy import text


def atualizar_banco():
    try:
        print("🔄 Atualizando banco de dados...")

        # 1. Adicionar coluna categoria_id se não existir
        with engine.connect() as conn:
            # Verificar se a coluna já existe
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'prestadores_servico' 
                AND COLUMN_NAME = 'categoria_id'
            """))

            if result.scalar() == 0:
                print("📝 Adicionando coluna categoria_id...")
                conn.execute(text("ALTER TABLE prestadores_servico ADD COLUMN categoria_id INT"))
                conn.execute(text(
                    "ALTER TABLE prestadores_servico ADD FOREIGN KEY (categoria_id) REFERENCES categorias_servico(id)"))
                conn.commit()
                print("✅ Coluna categoria_id adicionada!")
            else:
                print("✅ Coluna categoria_id já existe!")

        # 2. Criar tabela de categorias se não existir
        print("📝 Criando tabela categorias_servico...")
        Base.metadata.tables['categorias_servico'].create(bind=engine, checkfirst=True)

        print("🎉 Banco de dados atualizado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        return False


if __name__ == "__main__":
    atualizar_banco()