import psycopg2
from psycopg2.extras import RealDictCursor


def conectardb():
    con = psycopg2.connect(
        host='localhost',
        database='hortfrutas',
        user='postgres',
        password='root'
    )
    return con

def adicionarproduto(nome, marca, validade, preco, quantidade, caminho_completo_imagem):
    conexao = conectardb()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO produtos (nome, marca, validade, preco, quantidade, caminho_imagem) VALUES (%s, %s, %s, %s, %s, %s)",
                (nome, marca, validade, preco, quantidade, caminho_completo_imagem)
            )
            conexao.commit()
            return True
    except psycopg2.Error as e:
        print(f"Erro ao adicionar produto: {e}")
        conexao.rollback()
        return False
    finally:
        conexao.close()


def buscar_produto_por_nome(nome):
    conexao = conectardb()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM produtos WHERE nome = %s", (nome,))
            produto = cursor.fetchone()
            return produto
    finally:
        conexao.close()

def buscar_produto_por_id(product_id):
    conexao = conectardb()
    try:
        with conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM produtos WHERE id = %s", (product_id,))
            return cursor.fetchone()
    finally:
        conexao.close()

def atualizar_quantidade_produto(product_id, nova_quantidade):
    conexao = conectardb()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (nova_quantidade, product_id))
            conexao.commit()
            return cursor.rowcount > 0
    except Exception as e:
        conexao.rollback()
        return False
    finally:
        conexao.close()


def fetch_products_near_expiry(start_date, end_date):
    conexao = conectardb()
    try:
        with conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM produtos WHERE validade BETWEEN %s AND %s ORDER BY validade ASC
            """, (start_date, end_date))
            return cursor.fetchall()
    finally:
        conexao.close()

def listarprodutos():
    conexao = conectardb()
    cur = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, nome, marca, validade, preco, quantidade, caminho_imagem FROM produtos")
    produtos = cur.fetchall()
    conexao.close()
    return produtos




    lista_produtos = []
    for produto in produtos:
        lista_produtos.append({
            'nome': produto[0],
            'marca': produto[1],
            'validade': produto[2],
            'preco': produto[3],
            'quantidade': produto[4]
        })
    return lista_produtos


def inseriruser(email, senha, perfil):
    conexao = conectardb()
    cur = conexao.cursor()
    try:
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            print("E-mail já cadastrado.")
            return False

        print("Tentando inserir usuário...")
        cur.execute("INSERT INTO usuarios (email, senha, perfil) VALUES (%s, %s, %s)", (email, senha, perfil))
        conexao.commit()
        print("Usuário inserido com sucesso.")
        return True
    except psycopg2.Error as e:
        print(f"Erro ao tentar inserir usuário: {e}")
        conexao.rollback()
        return False
    finally:
        conexao.close()

def buscar_produto_por_nome(nome):
    conexao = conectardb()
    try:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM produtos WHERE nome = %s", (nome,))
            produto = cursor.fetchone()
            return produto
    finally:
        conexao.close()


def verificarlogin(email, senha):
    conexao = conectardb()
    cur = conexao.cursor()
    cur.execute("SELECT id, perfil FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
    usuario = cur.fetchone()
    conexao.close()
    if usuario:
        return {'id': usuario[0], 'perfil': usuario[1]}
    return None

def criar_tabelas():
    conexao = conectardb()
    cur = conexao.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            perfil VARCHAR(50) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            marca VARCHAR(255) NOT NULL,
            validade DATE NOT NULL,
            preco NUMERIC(10, 2) NOT NULL,
            quantidade INTEGER NOT NULL,
            caminho_imagem TEXT NOT NULL
        );
    """)
    conexao.commit()
    cur.close()
    conexao.close()

def listar_usuarios():
    conexao = conectardb()
    try:
        with conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM usuarios")
            return cursor.fetchall()
    finally:
        conexao.close()

def excluir_usuario(user_id):
    conexao = conectardb()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            if cursor.rowcount > 0:
                conexao.commit()
                return True
            else:
                conexao.rollback()
                return False
    except Exception as e:
        conexao.rollback()
        return False
    finally:
        conexao.close()

def excluir_produto(product_id):
    conexao = conectardb()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM produtos WHERE id = %s", (product_id,))
            if cursor.rowcount == 0:
                conexao.rollback()
                return False
            conexao.commit()
            return True
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao excluir produto: {e}")
        return False
    finally:
        conexao.close()




if __name__ == '__main__':
    criar_tabelas()
