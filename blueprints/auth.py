from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from database import db_session
from models import Usuario, PrestadorServico
from config import config
import logging

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Sistema de registro - ÚNICA VERSÃO"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            tipo = request.form.get('tipo', 'cliente')

            print(f"📝 Tentativa de registro: {nome}, {email}, {tipo}")

            # Validações básicas
            if not all([nome, email, senha]):
                flash('Por favor, preencha todos os campos obrigatórios.', 'warning')
                return render_template('auth/registro.html')

            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres.', 'warning')
                return render_template('auth/registro.html')

            # Verificar email
            existing_user = db_session.query(Usuario).filter_by(email=email).first()
            if existing_user:
                flash('Este email já está cadastrado.', 'warning')
                return render_template('auth/registro.html')

            # Criar usuário
            usuario = Usuario(
                nome=nome,
                email=email,
                tipo=tipo
            )
            usuario.set_senha(senha)

            db_session.add(usuario)
            db_session.commit()

            print(f"✅ Usuário criado: {usuario.id}")

            # Se for prestador
            if tipo == 'prestador':
                prestador = PrestadorServico(
                    usuario_id=usuario.id,
                    categoria=request.form.get('categoria', 'outros'),
                    especialidade=request.form.get('especialidade', ''),
                    disponivel='sim'
                )
                db_session.add(prestador)
                db_session.commit()
                print(f"✅ Prestador criado: {prestador.id}")

            login_user(usuario)
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db_session.rollback()
            print(f"❌ ERRO NO REGISTRO: {str(e)}")
            flash(f'Erro ao processar o cadastro: {str(e)}', 'danger')

    return render_template('auth/registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')

            usuario = db_session.query(Usuario).filter_by(email=email).first()

            if usuario and usuario.check_senha(senha):
                login_user(usuario)
                flash(f'Bem-vindo de volta, {usuario.nome}!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Email ou senha incorretos.', 'danger')

        except Exception as e:
            flash('Erro ao processar o login.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Alterar senha do usuário (cliente ou prestador)"""
    if request.method == 'POST':
        try:
            senha_atual = request.form.get('senha_atual', '')
            nova_senha = request.form.get('nova_senha', '')
            confirmar_senha = request.form.get('confirmar_senha', '')

            # Validar senha atual
            if not current_user.check_senha(senha_atual):
                flash('Senha atual incorreta.', 'error')
                return render_template('auth/alterar_senha.html')

            # Validar nova senha
            if nova_senha != confirmar_senha:
                flash('As novas senhas não coincidem.', 'error')
                return render_template('auth/alterar_senha.html')

            if len(nova_senha) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('auth/alterar_senha.html')

            # Alterar senha
            current_user.set_senha(nova_senha)
            db_session.commit()

            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db_session.rollback()
            flash(f'Erro ao alterar senha: {str(e)}', 'error')

    return render_template('auth/alterar_senha.html')


@auth_bp.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    """Solicitar redefinição de senha (esqueci minha senha)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()

            if not email:
                flash('Por favor, informe seu email.', 'error')
                return render_template('auth/redefinir_senha.html')

            usuario = db_session.query(Usuario).filter_by(email=email).first()

            if usuario:
                # Aqui você implementaria o envio de email
                # Por enquanto, apenas mostra mensagem
                flash('Se o email existir em nosso sistema, enviaremos instruções para redefinir sua senha.', 'info')
            else:
                # Por segurança, não revelamos se o email existe ou não
                flash('Se o email existir em nosso sistema, enviaremos instruções para redefinir sua senha.', 'info')

            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'Erro ao processar solicitação: {str(e)}', 'error')

    return render_template('auth/redefinir_senha.html')