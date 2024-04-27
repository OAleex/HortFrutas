from flask import Flask, request, session, redirect, url_for, render_template, jsonify, abort
from werkzeug.utils import secure_filename
from flask import render_template, session
import dao
from dao import criar_tabelas
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
secret_key = os.urandom(24)
app.secret_key = 'FLASK_SECRET_KEY'

@app.route('/')
def home():
    if 'perfil' in session:
        if session['perfil'] == 'ADM':
            return render_template('produtos_adm.html')
        else:
            return render_template('produtos_cliente.html')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'usuario_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        perfil = request.form['perfil']
        admin_code = request.form.get('admin-code')

        if perfil == 'ADM' and admin_code != 'rene_eh_brabo':
            return render_template('registro.html', error='Código de administração inválido.')

        if dao.inseriruser(email, senha, perfil):
            return redirect(url_for('login'))
        else:
            return render_template('registro.html', error='Falha ao registrar. O email já pode estar em uso.')

    return render_template('registro.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = dao.verificarlogin(email, senha)
        if usuario:
            session['usuario_id'] = usuario['id']
            session['perfil'] = usuario['perfil']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Email ou senha incorretos")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/products', methods=['GET'])
def products():
    if 'perfil' in session:
        produtos = dao.listarprodutos()
        return jsonify(produtos)
    else:
        return jsonify({'error': 'Não autorizado'}), 401







@app.route('/add-product', methods=['POST'])
def add_product():
    if 'perfil' in session and session['perfil'] == 'ADM':
        nome = request.form['nome']
        marca = request.form['marca']
        validade = request.form['validade']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        imagem = request.files['image']  # Aqui estava o erro de chave

        # Suponha que você tenha uma função para tratar o salvamento da imagem
        caminho_imagem = handle_image_upload(imagem)

        sucesso = dao.adicionarproduto(nome, marca, validade, preco, quantidade, caminho_imagem)
        if sucesso:
            return jsonify({"message": "Produto adicionado com sucesso!"}), 201
        else:
            return jsonify({"message": "Erro ao adicionar produto"}), 500
    else:
        abort(403)


pasta_imagens = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Produtos')
os.makedirs(pasta_imagens, exist_ok=True)

def handle_image_upload(imagem):
    filename = secure_filename(imagem.filename)
    caminho_imagem = os.path.join(pasta_imagens, filename)
    imagem.save(caminho_imagem)
    return caminho_imagem


@app.route('/produtos')
def produtos():
    if 'perfil' in session:
        if session['perfil'] == 'ADM':
            return render_template('produtos_adm.html')
        else:
            return render_template('produtos_cliente.html')
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True, port=5000)