# blueprints/servicos.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import PrestadorServico, Servico, CategoriaServico
from sqlalchemy import or_

servicos_bp = Blueprint('servicos', __name__, url_prefix='/servicos')


@servicos_bp.route('/buscar')
def buscar():
    """Busca de serviços com categorias dinâmicas"""
    try:
        categoria = request.args.get('categoria', '')
        q = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = 12

        # Buscar categorias do banco
        categorias = db_session.query(CategoriaServico).filter_by(ativa=True).order_by(CategoriaServico.ordem).all()

        # Consulta base
        query = db_session.query(PrestadorServico).filter_by(disponivel='sim')

        # Aplicar filtros
        if categoria:
            query = query.filter(PrestadorServico.categoria == categoria)

        if q:
            query = query.filter(
                or_(
                    PrestadorServico.especialidade.ilike(f'%{q}%'),
                    PrestadorServico.descricao.ilike(f'%{q}%'),
                    PrestadorServico.categoria.ilike(f'%{q}%')
                )
            )

        total = query.count()
        prestadores = query.offset((page - 1) * per_page).limit(per_page).all()

        search_stats = {
            'total': total,
            'pagina_atual': page,
            'total_paginas': (total + per_page - 1) // per_page,
            'categoria_selecionada': categoria,
            'categorias': categorias
        }

        return render_template('servicos/buscar.html',
                               prestadores=prestadores,
                               search_stats=search_stats)

    except Exception as e:
        print(f"Erro na busca: {e}")
        flash('Erro ao realizar busca', 'error')
        return redirect(url_for('servicos.buscar'))


@servicos_bp.route('/prestador/<int:prestador_id>')
def perfil_prestador(prestador_id):
    """Perfil do prestador - COM TEU LAYOUT PROFISSIONAL"""
    try:
        prestador = db_session.query(PrestadorServico).get(prestador_id)

        if not prestador:
            flash('Prestador não encontrado.', 'warning')
            return redirect(url_for('servicos.buscar'))

        servicos = db_session.query(Servico).filter_by(prestador_id=prestador_id).all()

        stats = {
            'total_servicos': len(servicos),
            'clientes_atendidos': len(servicos)
        }

        print(f"✅ Carregando perfil do prestador {prestador_id}")

        # AGORA usa o template Jinja2 que EXTENDE teu base.html
        return render_template('servicos/perfil.html',
                               prestador=prestador,
                               servicos=servicos,
                               stats=stats)

    except Exception as e:
        print(f"❌ Erro ao carregar perfil: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        flash('Erro ao carregar perfil', 'error')
        return redirect(url_for('servicos.buscar'))