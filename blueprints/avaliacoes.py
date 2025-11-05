# blueprints/avaliacoes.py
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import Avaliacao, Agendamento, Notificacao, PrestadorServico
from datetime import datetime

avaliacoes_bp = Blueprint('avaliacoes', __name__, url_prefix='/avaliacoes')


@avaliacoes_bp.route('/criar/<int:agendamento_id>', methods=['GET', 'POST'])  # ✅ CERTO
@login_required                                                               # ✅ CERTO
def criar_avaliacao(agendamento_id):
    """Página para avaliar um serviço concluído"""
    try:
        agendamento = db_session.query(Agendamento).get(agendamento_id)

        if not agendamento:
            flash('Agendamento não encontrado.', 'error')
            return redirect(url_for('main.dashboard'))

        # Verificar permissões
        if agendamento.cliente_id != current_user.id:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('main.dashboard'))

        # Verificar se o agendamento foi realizado
        if agendamento.status != 'realizado':
            flash('Apenas serviços concluídos podem ser avaliados.', 'warning')
            return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

        # Verificar se já existe avaliação
        avaliacao_existente = db_session.query(Avaliacao).filter_by(
            agendamento_id=agendamento_id
        ).first()

        if avaliacao_existente:
            flash('Este serviço já foi avaliado.', 'info')
            return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

        if request.method == 'POST':
            rating = request.form.get('rating')
            comentario = request.form.get('comentario', '').strip()
            anonima = request.form.get('anonima') == 'on'

            if not rating:
                flash('Por favor, selecione uma avaliação de 1 a 5 estrelas.', 'warning')
                return render_template('avaliacoes/avaliar.html', agendamento=agendamento)

            # Criar avaliação
            nova_avaliacao = Avaliacao(
                agendamento_id=agendamento_id,
                cliente_id=current_user.id,
                prestador_id=agendamento.prestador_id,
                rating=int(rating),
                comentario=comentario,
                anonima=anonima,
                data_avaliacao=datetime.utcnow()
            )

            db_session.add(nova_avaliacao)

            # Criar notificação para o prestador
            notificacao = Notificacao(
                usuario_id=agendamento.prestador.usuario.id,
                tipo='avaliacao',
                titulo='Nova Avaliação Recebida',
                mensagem=f'Você recebeu uma avaliação de {current_user.nome if not anonima else "um cliente"}',
                link_acao=f'/avaliacoes/minhas'
            )
            db_session.add(notificacao)

            db_session.commit()

            flash('Avaliação enviada com sucesso! Obrigado pelo feedback.', 'success')
            return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

        return render_template('avaliacoes/avaliar.html', agendamento=agendamento)

    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao processar avaliação: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@avaliacoes_bp.route('/minhas')
@login_required
def minhas_avaliacoes():
    """Página de avaliações do usuário"""
    try:
        if current_user.tipo == 'cliente':
            # Avaliações feitas pelo cliente
            avaliacoes = db_session.query(Avaliacao).filter_by(
                cliente_id=current_user.id
            ).order_by(Avaliacao.data_avaliacao.desc()).all()
            tipo = 'feitas'
        else:
            # Avaliações recebidas pelo prestador
            avaliacoes = db_session.query(Avaliacao).filter_by(
                prestador_id=current_user.prestador.id
            ).order_by(Avaliacao.data_avaliacao.desc()).all()
            tipo = 'recebidas'

        # Calcular estatísticas para prestadores
        estatisticas = None
        if current_user.tipo == 'prestador' and avaliacoes:
            total_avaliacoes = len(avaliacoes)
            media_rating = sum(av.rating for av in avaliacoes) / total_avaliacoes
            distribuicao = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            for av in avaliacoes:
                distribuicao[av.rating] += 1

            estatisticas = {
                'total_avaliacoes': total_avaliacoes,
                'media_rating': round(media_rating, 1),
                'distribuicao': distribuicao
            }

        return render_template('avaliacoes/minhas.html',
                               avaliacoes=avaliacoes,
                               tipo=tipo,
                               estatisticas=estatisticas)

    except Exception as e:
        flash('Erro ao carregar avaliações.', 'error')
        return render_template('avaliacoes/minhas.html', avaliacoes=[], tipo='feitas')


@avaliacoes_bp.route('/<int:avaliacao_id>/responder', methods=['POST'])
@login_required
def responder_avaliacao(avaliacao_id):
    """Responder a uma avaliação (prestador)"""
    try:
        avaliacao = db_session.query(Avaliacao).get(avaliacao_id)

        if not avaliacao or current_user.tipo != 'prestador' or avaliacao.prestador_id != current_user.prestador.id:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('avaliacoes.minhas_avaliacoes'))

        resposta = request.form.get('resposta', '').strip()

        if not resposta:
            flash('Por favor, escreva uma resposta.', 'warning')
            return redirect(url_for('avaliacoes.minhas_avaliacoes'))

        avaliacao.resposta_prestador = resposta
        avaliacao.data_resposta = datetime.utcnow()

        # Notificar o cliente
        notificacao = Notificacao(
            usuario_id=avaliacao.cliente_id,
            tipo='avaliacao',
            titulo='Resposta à Sua Avaliação',
            mensagem=f'{avaliacao.prestador.usuario.nome} respondeu sua avaliação',
            link_acao=f'/avaliacoes/minhas'
        )
        db_session.add(notificacao)

        db_session.commit()

        flash('Resposta enviada com sucesso!', 'success')
        return redirect(url_for('avaliacoes.minhas_avaliacoes'))

    except Exception as e:
        db_session.rollback()
        flash('Erro ao enviar resposta.', 'error')
        return redirect(url_for('avaliacoes.minhas_avaliacoes'))


@avaliacoes_bp.route('/api/estatisticas/<int:prestador_id>')
def estatisticas_prestador(prestador_id):
    """API: Estatísticas de avaliações de um prestador"""
    try:
        avaliacoes = db_session.query(Avaliacao).filter_by(
            prestador_id=prestador_id
        ).all()

        if not avaliacoes:
            return jsonify({
                'success': True,
                'estatisticas': {
                    'total_avaliacoes': 0,
                    'media_rating': 0,
                    'distribuicao': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                }
            })

        total_avaliacoes = len(avaliacoes)
        media_rating = sum(av.rating for av in avaliacoes) / total_avaliacoes
        distribuicao = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for av in avaliacoes:
            distribuicao[av.rating] += 1

        # Calcular percentuais
        distribuicao_percent = {
            stars: (count / total_avaliacoes) * 100
            for stars, count in distribuicao.items()
        }

        return jsonify({
            'success': True,
            'estatisticas': {
                'total_avaliacoes': total_avaliacoes,
                'media_rating': round(media_rating, 1),
                'distribuicao': distribuicao,
                'distribuicao_percent': distribuicao_percent
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@avaliacoes_bp.route('/api/ultimas/<int:prestador_id>')
def ultimas_avaliacoes(prestador_id):
    """API: Últimas avaliações de um prestador"""
    try:
        avaliacoes = db_session.query(Avaliacao).filter_by(
            prestador_id=prestador_id
        ).order_by(Avaliacao.data_avaliacao.desc()).limit(5).all()

        dados_avaliacoes = []
        for av in avaliacoes:
            dados_avaliacoes.append({
                'id': av.id,
                'cliente_nome': 'Cliente Anônimo' if av.anonima else av.cliente.nome,
                'rating': av.rating,
                'comentario': av.comentario,
                'data_avaliacao': av.data_avaliacao.strftime('%d/%m/%Y'),
                'resposta_prestador': av.resposta_prestador,
                'tem_resposta': av.resposta_prestador is not None
            })

        return jsonify({
            'success': True,
            'avaliacoes': dados_avaliacoes
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@avaliacoes_bp.route('/avaliar/<int:agendamento_id>', methods=['GET', 'POST'])
@login_required
def avaliar(agendamento_id):
    """Página para avaliar um serviço concluído"""
    try:
        print(f"🎯 DEBUG AVALIAÇÃO: Iniciando para agendamento {agendamento_id}")
        print(f"🎯 DEBUG: Usuário atual: {current_user.id} ({current_user.nome})")

        agendamento = db_session.query(Agendamento).get(agendamento_id)

        if not agendamento:
            print("❌ Agendamento não encontrado")
            flash('Agendamento não encontrado.', 'error')
            return redirect(url_for('main.dashboard'))

        print(f"🎯 DEBUG: Agendamento encontrado - Cliente: {agendamento.cliente_id}, Status: {agendamento.status}")

        # Verificar permissões
        if agendamento.cliente_id != current_user.id:
            print(f"❌ PERMISSÃO NEGADA: Cliente {current_user.id} != {agendamento.cliente_id}")
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('main.dashboard'))

        # Verificar se o agendamento foi realizado
        if agendamento.status != 'realizado':
            print(f"❌ STATUS INVÁLIDO: {agendamento.status} (precisa ser 'realizado')")
            flash('Apenas serviços concluídos podem ser avaliados.', 'warning')
            return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

        # Verificar se já existe avaliação
        avaliacao_existente = db_session.query(Avaliacao).filter_by(
            agendamento_id=agendamento_id
        ).first()

        if avaliacao_existente:
            print("❌ AVALIAÇÃO JÁ EXISTE")
            flash('Este serviço já foi avaliado.', 'info')
            return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

        if request.method == 'POST':
            print("📨 DEBUG: Recebido POST - Processando avaliação...")
            rating = request.form.get('rating')
            comentario = request.form.get('comentario', '').strip()
            anonima = request.form.get('anonima') == 'on'

            print(f"📨 DEBUG: Dados do form - Rating: '{rating}', Comentário: '{comentario}', Anônima: {anonima}")

            if not rating:
                print("❌ RATING VAZIO")
                flash('Por favor, selecione uma avaliação de 1 a 5 estrelas.', 'warning')
                return render_template('avaliacoes/avaliar.html', agendamento=agendamento)

            print("✅ DEBUG: Criando nova avaliação...")

            # Criar avaliação
            nova_avaliacao = Avaliacao(
                agendamento_id=agendamento_id,
                cliente_id=current_user.id,
                prestador_id=agendamento.prestador_id,
                rating=int(rating),
                comentario=comentario,
                anonima=anonima,
                data_avaliacao=datetime.utcnow()
            )

            db_session.add(nova_avaliacao)
            print("✅ DEBUG: Avaliação adicionada à sessão")

            # Criar notificação para o prestador
            notificacao = Notificacao(
                usuario_id=agendamento.prestador.usuario.id,
                tipo='avaliacao',
                titulo='Nova Avaliação Recebida',
                mensagem=f'Você recebeu uma avaliação de {current_user.nome if not anonima else "um cliente"}',
                link_acao=f'/avaliacoes/minhas'
            )
            db_session.add(notificacao)
            print("✅ DEBUG: Notificação criada")

            # COMMIT FINAL
            db_session.commit()
            print("🎉 DEBUG: COMMIT BEM-SUCEDIDO! Avaliação salva no banco.")

            flash('Avaliação enviada com sucesso! Obrigado pelo feedback.', 'success')
            return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

        return render_template('avaliacoes/avaliar.html', agendamento=agendamento)

    except Exception as e:
        print(f"💥 ERRO CRÍTICO: {str(e)}")
        import traceback
        print(f"💥 TRACEBACK: {traceback.format_exc()}")
        db_session.rollback()
        flash(f'Erro ao processar avaliação: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))