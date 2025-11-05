# blueprints/pagamentos.py
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import Pagamento, Agendamento, TransacaoFinanceira, PrestadorServico
from datetime import datetime

pagamentos_bp = Blueprint('pagamentos', __name__, url_prefix='/pagamentos')


@pagamentos_bp.route('/')
@login_required
def index():
    """Página principal de pagamentos"""
    try:
        if current_user.tipo == 'cliente':
            pagamentos = db_session.query(Pagamento).join(Agendamento).filter(
                Agendamento.cliente_id == current_user.id
            ).all()
        else:
            pagamentos = db_session.query(Pagamento).join(Agendamento).filter(
                Agendamento.prestador_id == current_user.prestador.id
            ).all()

        return render_template('pagamentos/index.html', pagamentos=pagamentos)

    except Exception as e:
        flash('Erro ao carregar pagamentos', 'error')
        return render_template('pagamentos/index.html', pagamentos=[])


@pagamentos_bp.route('/agendamento/<int:agendamento_id>')
@login_required
def pagamento_agendamento(agendamento_id):
    """Página de pagamento para um agendamento específico"""
    try:
        agendamento = db_session.query(Agendamento).get(agendamento_id)

        if not agendamento:
            flash('Agendamento não encontrado', 'error')
            return redirect(url_for('main.dashboard'))

        # Verificar permissão
        if current_user.tipo == 'cliente' and agendamento.cliente_id != current_user.id:
            flash('Acesso não autorizado', 'error')
            return redirect(url_for('main.dashboard'))

        # Verificar se já existe pagamento
        pagamento = db_session.query(Pagamento).filter_by(agendamento_id=agendamento_id).first()

        if not pagamento:
            # Criar pagamento pendente
            taxa_plataforma = agendamento.prestador.taxa_plataforma or 10.0
            valor_total = agendamento.servico.preco
            taxa_valor = (valor_total * taxa_plataforma) / 100
            valor_prestador = valor_total - taxa_valor

            pagamento = Pagamento(
                agendamento_id=agendamento_id,
                valor_total=valor_total,
                taxa_plataforma=taxa_plataforma,
                valor_prestador=valor_prestador,
                status='pendente'
            )
            db_session.add(pagamento)
            db_session.commit()

        return render_template('pagamentos/checkout.html',
                               pagamento=pagamento,
                               agendamento=agendamento)

    except Exception as e:
        flash(f'Erro ao processar pagamento: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@pagamentos_bp.route('/api/processar-pagamento', methods=['POST'])
@login_required
def processar_pagamento():
    """API: Processar pagamento (simulado)"""
    try:
        data = request.get_json()

        if not data or 'pagamento_id' not in data:
            return jsonify({'success': False, 'error': 'Dados inválidos'}), 400

        pagamento_id = data['pagamento_id']
        metodo_pagamento = data.get('metodo_pagamento', 'stripe')

        # Buscar pagamento
        pagamento = db_session.query(Pagamento).get(pagamento_id)
        if not pagamento:
            return jsonify({'success': False, 'error': 'Pagamento não encontrado'}), 404

        # Verificar permissão
        agendamento = pagamento.agendamento
        if current_user.tipo == 'cliente' and agendamento.cliente_id != current_user.id:
            return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403

        # Simular processamento de pagamento
        pagamento.status = 'pago'
        pagamento.metodo_pagamento = metodo_pagamento
        pagamento.data_pagamento = datetime.utcnow()
        pagamento.id_transacao = f"tx_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{pagamento_id}"

        # Atualizar status do agendamento
        agendamento.status = 'confirmado'

        # Criar transação financeira para o prestador
        transacao = TransacaoFinanceira(
            prestador_id=agendamento.prestador_id,
            tipo='credito',
            valor=pagamento.valor_prestador,
            descricao=f'Pagamento serviço: {agendamento.servico.titulo}',
            saldo_anterior=agendamento.prestador.saldo_disponivel or 0,
            saldo_posterior=(agendamento.prestador.saldo_disponivel or 0) + pagamento.valor_prestador,
            referencia=pagamento.id_transacao
        )

        # Atualizar saldo do prestador
        agendamento.prestador.saldo_disponivel = transacao.saldo_posterior
        agendamento.prestador.total_ganho = (agendamento.prestador.total_ganho or 0) + pagamento.valor_prestador

        db_session.add(transacao)
        db_session.commit()

        return jsonify({
            'success': True,
            'transacao_id': pagamento.id_transacao,
            'status': pagamento.status
        })

    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@pagamentos_bp.route('/api/configurar-taxa', methods=['POST'])
@login_required
def configurar_taxa():
    """API: Configurar taxa da plataforma para prestador"""
    try:
        if current_user.tipo != 'prestador' or not current_user.prestador:
            return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403

        data = request.get_json()
        taxa = data.get('taxa_plataforma', 10.0)

        # Validar taxa
        if not (0 <= taxa <= 30):
            return jsonify({'success': False, 'error': 'Taxa deve estar entre 0% e 30%'}), 400

        current_user.prestador.taxa_plataforma = taxa
        db_session.commit()

        return jsonify({
            'success': True,
            'taxa_configurada': taxa,
            'message': 'Taxa da plataforma atualizada com sucesso'
        })

    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@pagamentos_bp.route('/api/solicitar-saque', methods=['POST'])
@login_required
def solicitar_saque():
    """API: Solicitar saque de saldo"""
    try:
        if current_user.tipo != 'prestador' or not current_user.prestador:
            return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403

        data = request.get_json()
        valor_saque = float(data.get('valor', 0))

        prestador = current_user.prestador
        saldo_disponivel = prestador.saldo_disponivel or 0

        # Validar saque
        if valor_saque <= 0:
            return jsonify({'success': False, 'error': 'Valor de saque inválido'}), 400

        if valor_saque > saldo_disponivel:
            return jsonify({'success': False, 'error': 'Saldo insuficiente'}), 400

        # Criar transação de saque
        transacao = TransacaoFinanceira(
            prestador_id=prestador.id,
            tipo='debito',
            valor=valor_saque,
            descricao='Saque solicitado',
            saldo_anterior=saldo_disponivel,
            saldo_posterior=saldo_disponivel - valor_saque,
            referencia=f"saque_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        # Atualizar saldo
        prestador.saldo_disponivel = transacao.saldo_posterior

        db_session.add(transacao)
        db_session.commit()

        return jsonify({
            'success': True,
            'valor_sacado': valor_saque,
            'novo_saldo': prestador.saldo_disponivel,
            'transacao_id': transacao.referencia
        })

    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@pagamentos_bp.route('/api/transacoes')
@login_required
def listar_transacoes():
    """API: Listar transações financeiras"""
    try:
        if current_user.tipo == 'cliente':
            return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403

        prestador_id = current_user.prestador.id
        transacoes = db_session.query(TransacaoFinanceira).filter_by(
            prestador_id=prestador_id
        ).order_by(TransacaoFinanceira.data_transacao.desc()).all()

        dados_transacoes = []
        for trans in transacoes:
            dados_transacoes.append({
                'id': trans.id,
                'tipo': trans.tipo,
                'valor': trans.valor,
                'descricao': trans.descricao,
                'saldo_anterior': trans.saldo_anterior,
                'saldo_posterior': trans.saldo_posterior,
                'data_transacao': trans.data_transacao.isoformat(),
                'referencia': trans.referencia
            })

        return jsonify({
            'success': True,
            'transacoes': dados_transacoes,
            'saldo_atual': current_user.prestador.saldo_disponivel or 0
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pagamentos_bp.route('/historico')
@login_required
def historico():
    """Página de histórico de transações"""
    try:
        if current_user.tipo != 'prestador':
            flash('Acesso apenas para prestadores', 'error')
            return redirect(url_for('main.dashboard'))

        prestador_id = current_user.prestador.id
        transacoes = db_session.query(TransacaoFinanceira).filter_by(
            prestador_id=prestador_id
        ).order_by(TransacaoFinanceira.data_transacao.desc()).all()

        return render_template('pagamentos/historico.html',
                               transacoes=transacoes,
                               prestador=current_user.prestador)

    except Exception as e:
        flash('Erro ao carregar histórico', 'error')
        return render_template('pagamentos/historico.html', transacoes=[])