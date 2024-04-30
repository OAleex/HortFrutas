from flask import Flask, request, session, redirect, url_for, render_template, jsonify, abort, send_from_directory
from werkzeug.utils import secure_filename
import dao
from dao import criar_tabelas
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')

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


@app.route('/consume/<product_name>', methods=['GET'])
def consume_product(product_name):
    if 'perfil' not in session:
        return jsonify({'error': 'Não autorizado'}), 401

    produto = dao.buscar_produto_por_nome(product_name)
    if produto is None:
        return jsonify({'error': 'Produto não encontrado'}), 404

    return jsonify({'message': f'Você consumiu o produto: {product_name}'}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"message": "Already logged in"}), 200
        else:
            return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = dao.verificarlogin(email, senha)

        if usuario:
            session['usuario_id'] = usuario['id']
            session['perfil'] = usuario['perfil']

            if request.headers.get('Accept') == 'application/json':
                return jsonify({"message": "Login successful", "status": "success"}), 200
            else:
                return redirect(url_for('home'))
        else:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({"message": "Email or password incorrect", "status": "failure"}), 401
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
        imagem = request.files['image']
        caminho_imagem = handle_image_upload(imagem)
        sucesso = dao.adicionarproduto(nome, marca, validade, preco, quantidade, caminho_imagem)
        if sucesso:
            return jsonify({"message": "Produto adicionado com sucesso!"}), 201
        else:
            return jsonify({"message": "Erro ao adicionar produto"}), 500
    else:
        abort(403)


def handle_image_upload(imagem):
    filename = secure_filename(imagem.filename)
    caminho_completo_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    imagem.save(caminho_completo_imagem)
    return caminho_completo_imagem  # Agora retorna o caminho completo




@app.route('/Produtos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True, port=5000)
