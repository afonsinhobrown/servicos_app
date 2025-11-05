from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from database import db_session
from models import Notificacao

notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')

@notificacoes_bp.route('/')
@login_required
def listar():
    """Listar notificações do usuário"""
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 20

    notificacoes_query = db_session.query(Notificacao).filter_by(
        usuario_id=current_user.id
    ).order_by(Notificacao.data_criacao.desc())

    # Paginação manual
    total = notificacoes_query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina if total > 0 else 1
    offset = (pagina - 1) * por_pagina

    notificacoes = notificacoes_query.offset(offset).limit(por_pagina).all()

    # Marcar como lidas
    for notificacao in notificacoes:
        if not notificacao.lida:
            notificacao.lida = True
            notificacao.lida_em = datetime.now()

    db_session.commit()

    # Se for requisição AJAX (do dropdown), retornar apenas o HTML da lista
    if request.args.get('ajax'):
        return render_template('notificacoes/_lista.html', notificacoes=notificacoes)

    return render_template('notificacoes/listar.html',
                         notificacoes=notificacoes,
                         pagina=pagina,
                         total_paginas=total_paginas,
                         total=total)

@notificacoes_bp.route('/<int:notificacao_id>/ler')
@login_required
def ler(notificacao_id):
    """Marcar notificação como lida e redirecionar"""
    notificacao = db_session.query(Notificacao).get(notificacao_id)

    if not notificacao or notificacao.usuario_id != current_user.id:
        flash('Notificação não encontrada.', 'warning')
        return redirect(url_for('notificacoes.listar'))

    # Marcar como lida
    notificacao.lida = True
    notificacao.lida_em = datetime.now()
    db_session.commit()

    # Redirecionar para o link da notificação
    if notificacao.link_acao:
        return redirect(notificacao.link_acao)
    else:
        return redirect(url_for('notificacoes.listar'))

@notificacoes_bp.route('/marcar-todas-lidas', methods=['POST'])
@login_required
def marcar_todas_lidas():
    """Marcar todas as notificações como lidas"""
    db_session.query(Notificacao).filter_by(
        usuario_id=current_user.id,
        lida=False
    ).update({'lida': True, 'lida_em': datetime.now()})

    db_session.commit()
    flash('Todas as notificações marcadas como lidas.', 'success')
    return redirect(url_for('notificacoes.listar'))

@notificacoes_bp.route('/api/nao-lidas')
@login_required
def api_nao_lidas():
    """API: Contar notificações não lidas"""
    count = db_session.query(Notificacao).filter_by(
        usuario_id=current_user.id,
        lida=False
    ).count()

    return jsonify({'nao_lidas': count})

@notificacoes_bp.route('/<int:notificacao_id>/excluir', methods=['POST'])
@login_required
def excluir(notificacao_id):
    """Excluir notificação"""
    notificacao = db_session.query(Notificacao).get(notificacao_id)

    if not notificacao or notificacao.usuario_id != current_user.id:
        flash('Notificação não encontrada.', 'warning')
        return redirect(url_for('notificacoes.listar'))

    db_session.delete(notificacao)
    db_session.commit()

    flash('Notificação excluída.', 'success')
    return redirect(url_for('notificacoes.listar'))