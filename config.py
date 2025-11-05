import os


class Config:
    """Configurações principais da aplicação"""

    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'servicos_pro_chave_dev_2024'

    # Banco de Dados
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:STAE2019@localhost/plataforma_servicos"

    # Configurações do Flask
    DEBUG = True

    # Categorias disponíveis
    CATEGORIAS = [
        'medico', 'psicologo', 'personal_trainer',
        'cozinheiro', 'pastor', 'advogado', 'consultor', 'outros'
    ]

    # Níveis de serviço
    NIVEL_SERVICOS = ['basico', 'intermediario', 'avancado', 'premium']

    # Status de agendamento
    STATUS_AGENDAMENTO = ['pendente', 'confirmado', 'realizado', 'cancelado']


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:STAE2019@localhost/plataforma_servicos"


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    # Em produção, usar variáveis de ambiente
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')


# Configuração ativa
config = DevelopmentConfig