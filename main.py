from flask import Flask, render_template, request, flash, url_for, redirect
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\siteFinanceiroBanco\BANCODADOS.FDB'
user = 'sysdba'
password = 'sysdba'

@app.route('/inicio', methods=['GET'])
def inicio():
    total_receita = 0
    total_despesa = 0
    # Verifica se o usuário está autenticado
    if 'id_usuario' not in session:
        flash('Você precisa estar logado no sistema.')
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT coalesce(VALOR_RECEITA,0) FROM RECEITA where id_usuario = ?', (id_usuario,))
        for row in cursor.fetchall():
            total_receita = total_receita + row[0]

        cursor.execute('SELECT coalesce(VALOR_DESPESA,0) FROM DESPESA where id_usuario = ?', (id_usuario,))
        for row in cursor.fetchall():
            total_despesa = total_despesa + row[0]

        total_perda_lucro = total_receita - total_despesa
    except Exception as e:
        total_receita = 0
        total_despesa = 0
        print(f"Erro ao buscar total_receita: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
    finally:
        cursor.close()
    # Aqui você pode renderizar um template ou retornar os valores
    total_receita = f"{total_receita:.2f}"
    total_despesa = f"{total_despesa:.2f}"
    total_perda_lucro = f"{total_perda_lucro:.2f}"
    return render_template('index.html', total_receita=total_receita, total_despesa=total_despesa, total_perda_lucro=total_perda_lucro)


@app.route('/cria_usuario', methods=['GET'])
def cria_usuario():
    return render_template('adiciona_usuario.html')

# Rota para adicionar usuário
@app.route('/adiciona_usuario', methods=['POST'])
def adiciona_usuario():
    data = request.form
    nome = data['nome']
    email = data['email']
    senha = data['senha']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT FIRST 1 id_usuario FROM USUARIO WHERE EMAIL = ?', (email,))
        if cursor.fetchone() is not None:
            flash('Este email já está sendo usado!')
            return redirect(url_for('cria_usuario'))

        cursor.execute("INSERT INTO Usuario (nome, email, senha) VALUES (?, ?, ?)",
                       (nome, email, senha))
        con.commit()
    finally:
        cursor.close()
    flash('Usuario adicionado com sucesso!')
    return redirect(url_for('login'))

# Rota de Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()
        try:
            cursor.execute("SELECT id_usuario,nome FROM Usuario WHERE email = ? AND senha = ?", (email, senha,))
            usuario = cursor.fetchone()
        except Exception as e:
            flash(f'Erro ao acessar o banco de dados: {e}')  # Mensagem de erro para o usuário
            return redirect(url_for('login'))  # Redireciona de volta ao login
        finally:
            cursor.close()

        if usuario:
            session['id_usuario'] = usuario[0]  # Armazena o ID do usuário na sessão
            session['nome'] = usuario[1] #nome do mané
            return redirect(url_for('inicio'))
        else:
            flash('Email ou senha incorretos!')

    return render_template('login.html')

# Rota de Logout
@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('login'))
