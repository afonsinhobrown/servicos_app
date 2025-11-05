from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

Base = declarative_base()


class Usuario(Base, UserMixin):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(20), default='cliente')
    telefone = Column(String(20))
    cidade = Column(String(100))
    bairro = Column(String(100))
    coordenadas = Column(String(100))  # lat,lng
    avatar_url = Column(String(500))
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime)
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    prestador = relationship("PrestadorServico", back_populates="usuario", uselist=False)
    agendamentos_cliente = relationship("Agendamento", foreign_keys="Agendamento.cliente_id", back_populates="cliente")
    mensagens_enviadas = relationship("Mensagem", foreign_keys="Mensagem.remetente_id", back_populates="remetente")
    avaliacoes_feitas = relationship("Avaliacao", foreign_keys="Avaliacao.cliente_id", back_populates="cliente")
    notificacoes = relationship("Notificacao", back_populates="usuario")
    tickets_suporte = relationship("TicketSuporte", back_populates="usuario")
    transacoes = relationship("TransacaoFinanceira", back_populates="usuario")

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.email}>'


class CategoriaServico(Base):
    __tablename__ = 'categorias_servico'

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text)
    icone = Column(String(50))
    ativa = Column(Boolean, default=True)
    ordem = Column(Integer, default=0)

    # Relacionamentos
    prestadores = relationship("PrestadorServico", back_populates="categoria_obj")

    def __repr__(self):
        return f'<Categoria {self.nome}>'


class PrestadorServico(Base):
    __tablename__ = 'prestadores_servico'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias_servico.id'))
    categoria = Column(String(50), nullable=False)
    especialidade = Column(String(100), nullable=False)
    descricao = Column(Text)
    experiencia = Column(Integer, default=0)
    valor_hora = Column(Float, default=0.0)
    disponivel = Column(String(3), default='sim')
    taxa_plataforma = Column(Float, default=10.0)
    raio_atuacao = Column(Integer, default=10)
    disponivel_online = Column(Boolean, default=False)
    verificado = Column(Boolean, default=False)
    saldo_disponivel = Column(Float, default=0.0)
    total_ganho = Column(Float, default=0.0)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="prestador")
    servicos = relationship("Servico", back_populates="prestador")
    agendamentos = relationship("Agendamento", foreign_keys="Agendamento.prestador_id", back_populates="prestador")
    avaliacoes_recebidas = relationship("Avaliacao", foreign_keys="Avaliacao.prestador_id", back_populates="prestador")
    documentos = relationship("DocumentoPrestador", back_populates="prestador")
    transacoes_financeiras = relationship("TransacaoFinanceira", back_populates="prestador")
    categoria_obj = relationship("CategoriaServico", back_populates="prestadores")

    def __repr__(self):
        return f'<Prestador {self.especialidade}>'


class Servico(Base):
    __tablename__ = 'servicos'

    id = Column(Integer, primary_key=True)
    prestador_id = Column(Integer, ForeignKey('prestadores_servico.id'), nullable=False)
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    nivel = Column(String(20), nullable=False)
    duracao = Column(Integer, default=60)
    preco = Column(Float, nullable=False)
    tags = Column(JSON)  # ['urgente', 'domicilio', 'online']
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    prestador = relationship("PrestadorServico", back_populates="servicos")
    agendamentos = relationship("Agendamento", back_populates="servico")

    def __repr__(self):
        return f'<Servico {self.titulo}>'


class Agendamento(Base):
    __tablename__ = 'agendamentos'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    prestador_id = Column(Integer, ForeignKey('prestadores_servico.id'), nullable=False)
    servico_id = Column(Integer, ForeignKey('servicos.id'), nullable=False)
    data_agendamento = Column(DateTime, nullable=False)
    status = Column(String(20), default='pendente')  # pendente, confirmado, em_andamento, realizado, cancelado
    observacoes = Column(Text)
    endereco_servico = Column(Text)
    modalidade = Column(String(20), default='presencial')  # presencial, online
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="agendamentos_cliente")
    prestador = relationship("PrestadorServico", foreign_keys=[prestador_id], back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
    conversa = relationship("Conversa", back_populates="agendamento", uselist=False)
    avaliacao = relationship("Avaliacao", back_populates="agendamento", uselist=False)
    pagamento = relationship("Pagamento", back_populates="agendamento", uselist=False)

    def __repr__(self):
        return f'<Agendamento {self.status}>'


class Conversa(Base):
    __tablename__ = 'conversas'

    id = Column(Integer, primary_key=True)
    agendamento_id = Column(Integer, ForeignKey('agendamentos.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    prestador_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ultima_mensagem = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    agendamento = relationship("Agendamento", back_populates="conversa")
    mensagens = relationship("Mensagem", back_populates="conversa")
    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    prestador = relationship("Usuario", foreign_keys=[prestador_id])

    def __repr__(self):
        return f'<Conversa {self.id}>'


class Mensagem(Base):
    __tablename__ = 'mensagens'

    id = Column(Integer, primary_key=True)
    conversa_id = Column(Integer, ForeignKey('conversas.id'), nullable=False)
    remetente_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    conteudo = Column(Text, nullable=False)
    tipo = Column(String(20), default='texto')  # texto, imagem, arquivo, sistema
    arquivo_url = Column(String(500))
    data_envio = Column(DateTime, default=datetime.utcnow)
    lida = Column(Boolean, default=False)

    # Relacionamentos
    conversa = relationship("Conversa", back_populates="mensagens")
    remetente = relationship("Usuario", foreign_keys=[remetente_id], back_populates="mensagens_enviadas")

    def __repr__(self):
        return f'<Mensagem {self.id}>'


class Pagamento(Base):
    __tablename__ = 'pagamentos'

    id = Column(Integer, primary_key=True)
    agendamento_id = Column(Integer, ForeignKey('agendamentos.id'), nullable=False)
    valor_total = Column(Float, nullable=False)
    taxa_plataforma = Column(Float, default=10.0)  # %
    valor_prestador = Column(Float, nullable=False)  # valor_total - taxa
    status = Column(String(20), default='pendente')  # pendente, pago, falhado, reembolsado
    metodo_pagamento = Column(String(50))  # stripe, mercadopago, etc
    id_transacao = Column(String(100))  # ID do gateway de pagamento
    data_pagamento = Column(DateTime)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    agendamento = relationship("Agendamento", back_populates="pagamento")

    def __repr__(self):
        return f'<Pagamento {self.status}>'


class Avaliacao(Base):
    __tablename__ = 'avaliacoes'

    id = Column(Integer, primary_key=True)
    agendamento_id = Column(Integer, ForeignKey('agendamentos.id'))
    cliente_id = Column(Integer, ForeignKey('usuarios.id'))
    prestador_id = Column(Integer, ForeignKey('prestadores_servico.id'))
    rating = Column(Integer)  # 1-5 estrelas
    comentario = Column(Text)
    anonima = Column(Boolean, default=False)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)
    resposta_prestador = Column(Text)
    data_resposta = Column(DateTime)

    # Relacionamentos
    agendamento = relationship("Agendamento", back_populates="avaliacao")
    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="avaliacoes_feitas")
    prestador = relationship("PrestadorServico", foreign_keys=[prestador_id], back_populates="avaliacoes_recebidas")

    def __repr__(self):
        return f'<Avaliacao {self.rating} estrelas>'


class Notificacao(Base):
    __tablename__ = 'notificacoes'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    tipo = Column(String(50))  # 'agendamento', 'mensagem', 'pagamento', 'avaliacao', 'sistema'
    titulo = Column(String(200))
    mensagem = Column(Text)
    lida = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    link_acao = Column(String(500))  # URL para ação

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="notificacoes")

    def __repr__(self):
        return f'<Notificacao {self.tipo}>'


class TransacaoFinanceira(Base):
    __tablename__ = 'transacoes_financeiras'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    prestador_id = Column(Integer, ForeignKey('prestadores_servico.id'))
    tipo = Column(String(20))  # 'credito', 'debito', 'taxa'
    valor = Column(Float)
    descricao = Column(String(200))
    saldo_anterior = Column(Float)
    saldo_posterior = Column(Float)
    referencia = Column(String(100))  # ID do pagamento/agendamento
    data_transacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="transacoes")
    prestador = relationship("PrestadorServico", back_populates="transacoes_financeiras")

    def __repr__(self):
        return f'<Transacao {self.tipo} - {self.valor}>'


# KEEP ONLY ONE TicketSuporte CLASS - REMOVED THE DUPLICATE
class TicketSuporte(Base):
    __tablename__ = 'tickets_suporte'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    assunto = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(50))
    status = Column(String(20), default='aberto')  # aberto, em_andamento, respondido, fechado
    prioridade = Column(String(20), default='media')  # baixa, media, alta, urgente
    data_abertura = Column(DateTime, default=datetime.utcnow)
    data_resolucao = Column(DateTime)
    resolucao = Column(Text)

    # Relacionamentos CORRIGIDOS
    usuario = relationship("Usuario", back_populates="tickets_suporte")
    respostas = relationship("TicketResposta", back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<TicketSuporte {self.assunto}>'

class TicketResposta(Base):
    __tablename__ = 'tickets_respostas'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets_suporte.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    resposta = Column(Text, nullable=False)
    data_resposta = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos CORRETOS
    ticket = relationship("TicketSuporte", back_populates="respostas")
    usuario = relationship("Usuario")

    def __repr__(self):
        return f'<TicketResposta {self.id}>'


class DocumentoPrestador(Base):
    __tablename__ = 'documentos_prestador'

    id = Column(Integer, primary_key=True)
    prestador_id = Column(Integer, ForeignKey('prestadores_servico.id'))
    tipo_documento = Column(String(50))  # 'bi', 'certificado', 'cv', 'comprovativo'
    nome_arquivo = Column(String(255))
    arquivo_url = Column(String(500))
    status_verificacao = Column(String(20), default='pendente')  # pendente, aprovado, rejeitado
    observacoes = Column(Text)
    data_upload = Column(DateTime, default=datetime.utcnow)
    data_verificacao = Column(DateTime)

    # Relacionamentos
    prestador = relationship("PrestadorServico", back_populates="documentos")

    def __repr__(self):
        return f'<Documento {self.tipo_documento}>'


class ConfiguracaoPlataforma(Base):
    __tablename__ = 'configuracoes_plataforma'

    id = Column(Integer, primary_key=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    tipo = Column(String(20))  # 'string', 'number', 'boolean', 'json'
    descricao = Column(Text)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Configuracao {self.chave}>'