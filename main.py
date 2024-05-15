from flask import Flask, request, session, redirect, url_for, render_template, jsonify, flash
from werkzeug.utils import secure_filename, send_from_directory
import dao
import os
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')

def is_logged_in():
    return 'usuario_id' in session

def is_admin():
    return session.get('perfil') == 'ADM'

def get_logged_user_id():
    return session.get('usuario_id', None)

@app.route('/')
def home():
    if not is_logged_in():
        return redirect(url_for('login'))
    if is_admin():
        return render_template('produtos_adm.html')
    return render_template('produtos_cliente.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('registro.html')

    email = request.form.get('email')
    senha = request.form.get('senha')
    perfil = request.form.get('perfil')
    admin_code = request.form.get('admin-code', '')
    if perfil == 'ADM' and admin_code != 'rene_eh_brabo':
        return render_template('registro.html', error='Código de administração inválido.')
    if dao.inseriruser(email, senha, perfil):
        return redirect(url_for('login'))
    return render_template('registro.html', error='Falha ao registrar. O email já pode estar em uso.')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"message": "Already logged in"}), 200
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
            return redirect(url_for('home'))
        else:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({"message": "Email or password incorrect", "status": "failure"}), 401
            return render_template('login.html', error="Email ou senha incorretos")

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/products', methods=['GET'])
def products():
    if not is_logged_in():
        return jsonify({'error': 'Não autorizado'}), 401
    produtos = dao.listarprodutos()
    return jsonify(produtos)

@app.route('/add-product', methods=['POST'])
def add_product():
    if not is_admin():
        os.abort(403)
    nome = request.form.get('nome')
    marca = request.form.get('marca')
    validade = request.form.get('validade')
    preco = request.form.get('preco')
    quantidade = request.form.get('quantidade')
    imagem = request.files['image']
    caminho_imagem = handle_image_upload(imagem)
    if dao.adicionarproduto(nome, marca, validade, preco, quantidade, caminho_imagem):
        flash("Produto adicionado com sucesso!", "success")
        return redirect(url_for('home'))
    flash("Erro ao adicionar produto", "error")
    return redirect(url_for('home'))

@app.route('/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if not is_admin():
        return jsonify({"error": "Acesso negado"}), 403
    if dao.excluir_produto(product_id):
        return jsonify({"message": "Produto excluído com sucesso!"}), 200
    return jsonify({"message": "Erro ao excluir produto"}), 500

@app.route('/admin/manage-users', methods=['GET'])
def manage_users():
    if not is_admin():
        return redirect(url_for('login'))
    usuarios = dao.listar_usuarios()
    return render_template('adm_gerenciar_usuarios.html', usuarios=usuarios)


@app.route('/admin/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not is_admin():
        return jsonify({"error": "Acesso negado"}), 403

    logged_user_id = get_logged_user_id()
    if user_id == logged_user_id:
        return jsonify({"error": "Operação não permitida. Você não pode excluir sua própria conta."}), 403

    if dao.excluir_usuario(user_id):
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro ao excluir usuário"}), 500

@app.route('/order-product-by-name/<product_name>/<int:quantity>', methods=['GET'])
def order_product_by_name(product_name, quantity):
    if not is_logged_in():
        return jsonify({'error': 'Não autorizado'}), 403

    product = dao.buscar_produto_por_nome(product_name)
    if product is None:
        return jsonify({'error': 'Produto nao encontrado'}), 404

    if product['quantidade'] < quantity:
        return jsonify({'error': 'Quantidade solicitada nao disponivel'}), 400

    success = dao.atualizar_quantidade_produto(product['id'], product['quantidade'] - quantity)
    if success:
        return jsonify({"message": "Pedido realizado com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao realizar pedido"}), 500

@app.route('/products-near-expiry', methods=['GET'])
def products_near_expiry():
    if not is_logged_in():
        return jsonify({'error': 'Não autorizado'}), 401

    today = datetime.now().date()
    expiry_limit = today + timedelta(days=7)

    try:
        products = dao.fetch_products_near_expiry(today, expiry_limit)
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": "Erro ao buscar produtos: " + str(e)}), 500


def handle_image_upload(imagem):
    filename = secure_filename(imagem.filename)
    caminho_completo_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    imagem.save(caminho_completo_imagem)
    return caminho_completo_imagem

@app.route('/Produtos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    dao.criar_tabelas()
    app.run(debug=True, port=5000)