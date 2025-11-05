# blueprints/api.py
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from database import db_session
from models import PrestadorServico, Servico, Usuario, Agendamento
from config import config

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==================== API PRESTADORES ====================

@api_bp.route('/prestadores', methods=['GET'])
def listar_prestadores():
    """API: Lista todos os prestadores"""
    try:
        # Parâmetros da query
        categoria = request.args.get('categoria', '')
        especialidade = request.args.get('especialidade', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 12)), 50)  # Max 50 por página

        # Query base
        query = db_session.query(PrestadorServico).filter_by(disponivel='sim')

        # Aplicar filtros
        if categoria:
            query = query.filter_by(categoria=categoria)
        if especialidade:
            query = query.filter(PrestadorServico.especialidade.ilike(f'%{especialidade}%'))

        # Paginação
        total = query.count()
        prestadores = query.offset((page - 1) * per_page).limit(per_page).all()

        # Serializar dados
        dados = []
        for prestador in prestadores:
            dados.append({
                'id': prestador.id,
                'nome': prestador.usuario.nome,
                'email': prestador.usuario.email,
                'telefone': prestador.usuario.telefone,
                'categoria': prestador.categoria,
                'especialidade': prestador.especialidade,
                'descricao': prestador.descricao,
                'experiencia': prestador.experiencia,
                'valor_hora': float(prestador.valor_hora) if prestador.valor_hora else None,
                'disponivel': prestador.disponivel == 'sim',
                'avatar_url': f"/static/avatars/{prestador.categoria}.jpg",
                'avaliacao_media': 4.8,  # Placeholder
                'total_avaliacoes': 124  # Placeholder
            })

        return jsonify({
            'success': True,
            'data': dados,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            },
            'filters': {
                'categoria': categoria,
                'especialidade': especialidade
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/prestadores/<int:prestador_id>', methods=['GET'])
def obter_prestador(prestador_id):
    """API: Obter detalhes de um prestador específico"""
    try:
        prestador = db_session.query(PrestadorServico).get(prestador_id)

        if not prestador:
            return jsonify({
                'success': False,
                'error': 'Prestador não encontrado'
            }), 404

        # Obter serviços do prestador
        servicos = db_session.query(Servico).filter_by(prestador_id=prestador_id).all()

        dados_servicos = []
        for servico in servicos:
            dados_servicos.append({
                'id': servico.id,
                'titulo': servico.titulo,
                'descricao': servico.descricao,
                'nivel': servico.nivel,
                'duracao': servico.duracao,
                'preco': float(servico.preco)
            })

        dados_prestador = {
            'id': prestador.id,
            'nome': prestador.usuario.nome,
            'email': prestador.usuario.email,
            'telefone': prestador.usuario.telefone,
            'categoria': prestador.categoria,
            'especialidade': prestador.especialidade,
            'descricao': prestador.descricao,
            'experiencia': prestador.experiencia,
            'valor_hora': float(prestador.valor_hora) if prestador.valor_hora else None,
            'disponivel': prestador.disponivel == 'sim',
            'servicos': dados_servicos,
            'estatisticas': {
                'total_servicos': len(servicos),
                'avaliacao_media': 4.8,
                'total_avaliacoes': 124,
                'clientes_atendidos': 89
            }
        }

        return jsonify({
            'success': True,
            'data': dados_prestador
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== API SERVIÇOS ====================

@api_bp.route('/servicos', methods=['GET'])
def listar_servicos():
    """API: Lista todos os serviços"""
    try:
        categoria = request.args.get('categoria', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 12)), 50)

        query = db_session.query(Servico).join(PrestadorServico)

        if categoria:
            query = query.filter(PrestadorServico.categoria == categoria)

        total = query.count()
        servicos = query.offset((page - 1) * per_page).limit(per_page).all()

        dados = []
        for servico in servicos:
            dados.append({
                'id': servico.id,
                'titulo': servico.titulo,
                'descricao': servico.descricao,
                'nivel': servico.nivel,
                'duracao': servico.duracao,
                'preco': float(servico.preco),
                'prestador': {
                    'id': servico.prestador.id,
                    'nome': servico.prestador.usuario.nome,
                    'categoria': servico.prestador.categoria,
                    'especialidade': servico.prestador.especialidade
                }
            })

        return jsonify({
            'success': True,
            'data': dados,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== API AGENDAMENTOS ====================

@api_bp.route('/agendamentos', methods=['GET'])
@login_required
def listar_agendamentos_usuario():
    """API: Lista agendamentos do usuário logado"""
    try:
        agendamentos = db_session.query(Agendamento).filter_by(cliente_id=current_user.id).all()

        dados = []
        for agendamento in agendamentos:
            dados.append({
                'id': agendamento.id,
                'servico': agendamento.servico.titulo,
                'prestador': agendamento.prestador.usuario.nome,
                'data_agendamento': agendamento.data_agendamento.isoformat() if agendamento.data_agendamento else None,
                'status': agendamento.status,
                'observacoes': agendamento.observacoes,
                'criado_em': agendamento.criado_em.isoformat() if agendamento.criado_em else None
            })

        return jsonify({
            'success': True,
            'data': dados
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/agendamentos', methods=['POST'])
@login_required
def criar_agendamento():
    """API: Criar novo agendamento"""
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'success': False,
                'error': 'Dados JSON necessários'
            }), 400

        # Validar dados obrigatórios
        required_fields = ['servico_id', 'data_agendamento']
        for field in required_fields:
            if field not in dados:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório faltando: {field}'
                }), 400

        # Verificar se serviço existe
        servico = db_session.query(Servico).get(dados['servico_id'])
        if not servico:
            return jsonify({
                'success': False,
                'error': 'Serviço não encontrado'
            }), 404

        # Criar agendamento
        agendamento = Agendamento(
            cliente_id=current_user.id,
            prestador_id=servico.prestador_id,
            servico_id=dados['servico_id'],
            data_agendamento=dados['data_agendamento'],
            observacoes=dados.get('observacoes', ''),
            status='pendente'
        )

        db_session.add(agendamento)
        db_session.commit()

        return jsonify({
            'success': True,
            'message': 'Agendamento criado com sucesso',
            'data': {
                'id': agendamento.id,
                'status': agendamento.status
            }
        }), 201

    except Exception as e:
        db_session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== API ESTATÍSTICAS ====================

@api_bp.route('/estatisticas', methods=['GET'])
def estatisticas_gerais():
    """API: Estatísticas gerais da plataforma"""
    try:
        total_prestadores = db_session.query(PrestadorServico).filter_by(disponivel='sim').count()
        total_servicos = db_session.query(Servico).count()
        total_agendamentos = db_session.query(Agendamento).count()

        # Contar por categoria
        categorias_count = {}
        for cat in config.CATEGORIAS:
            count = db_session.query(PrestadorServico).filter_by(
                categoria=cat,
                disponivel='sim'
            ).count()
            categorias_count[cat] = count

        return jsonify({
            'success': True,
            'data': {
                'total_prestadores': total_prestadores,
                'total_servicos': total_servicos,
                'total_agendamentos': total_agendamentos,
                'categorias': categorias_count,
                'avaliacao_media_plataforma': 4.7,
                'crescimento_mensal': '15%'
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== API CATEGORIAS ====================

@api_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """API: Lista todas as categorias disponíveis"""
    try:
        categorias = []
        for cat in config.CATEGORIAS:
            count = db_session.query(PrestadorServico).filter_by(
                categoria=cat,
                disponivel='sim'
            ).count()

            categorias.append({
                'id': cat,
                'nome': cat.replace('_', ' ').title(),
                'total_prestadores': count,
                'icone': f'bi-{cat}'  # Placeholder para ícones
            })

        return jsonify({
            'success': True,
            'data': categorias
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500





# ==================== API BUSCA AVANÇADA ====================

@api_bp.route('/busca', methods=['GET'])
def busca_avancada():
    """API: Busca avançada por prestadores e serviços"""
    try:
        termo = request.args.get('q', '')
        categoria = request.args.get('categoria', '')
        preco_min = request.args.get('preco_min')
        preco_max = request.args.get('preco_max')
        experiencia_min = request.args.get('experiencia_min')

        if not termo and not categoria:
            return jsonify({
                'success': False,
                'error': 'Termo de busca ou categoria é necessário'
            }), 400

        # Buscar prestadores
        query_prestadores = db_session.query(PrestadorServico).filter_by(disponivel='sim')

        if termo:
            query_prestadores = query_prestadores.filter(
                (PrestadorServico.especialidade.ilike(f'%{termo}%')) |
                (PrestadorServico.descricao.ilike(f'%{termo}%')) |
                (PrestadorServico.usuario.has(Usuario.nome.ilike(f'%{termo}%')))
            )

        if categoria:
            query_prestadores = query_prestadores.filter_by(categoria=categoria)

        if preco_min:
            query_prestadores = query_prestadores.filter(PrestadorServico.valor_hora >= float(preco_min))

        if preco_max:
            query_prestadores = query_prestadores.filter(PrestadorServico.valor_hora <= float(preco_max))

        if experiencia_min:
            query_prestadores = query_prestadores.filter(PrestadorServico.experiencia >= int(experiencia_min))

        prestadores = query_prestadores.all()

        # Serializar resultados
        resultados = []
        for prestador in prestadores:
            resultados.append({
                'tipo': 'prestador',
                'id': prestador.id,
                'nome': prestador.usuario.nome,
                'categoria': prestador.categoria,
                'especialidade': prestador.especialidade,
                'experiencia': prestador.experiencia,
                'valor_hora': float(prestador.valor_hora) if prestador.valor_hora else None,
                'descricao': prestador.descricao
            })

        return jsonify({
            'success': True,
            'data': {
                'resultados': resultados,
                'total': len(resultados),
                'termo_busca': termo,
                'filtros_aplicados': {
                    'categoria': categoria,
                    'preco_min': preco_min,
                    'preco_max': preco_max,
                    'experiencia_min': experiencia_min
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500





