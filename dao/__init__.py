import psycopg2


def conectardb():
    con = psycopg2.connect(
        host='localhost',
        database='hortfrutas',
        user='postgres',
        password='root'
    )
    return con

def adicionarproduto(nome, marca, validade, preco, quantidade, caminho_imagem):
    conexao = conectardb()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO produtos (nome, marca, validade, preco, quantidade, caminho_imagem) VALUES (%s, %s, %s, %s, %s, %s)",
                (nome, marca, validade, preco, quantidade, caminho_imagem)
            )
            conexao.commit()
            return True
    except psycopg2.Error as e:
        print(f"Erro ao adicionar produto: {e}")
        conexao.rollback()
        return False
    finally:
        conexao.close()


def listarprodutos():
    conexao = conectardb()
    cur = conexao.cursor()
    cur.execute("SELECT nome, marca, validade, preco, quantidade FROM produtos")
    produtos = cur.fetchall()
    conexao.close()

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
        cur.execute("INSERT INTO usuarios (email, senha, perfil) VALUES (%s, %s, %s)", (email, senha, perfil))
        conexao.commit()
        return True
    except psycopg2.IntegrityError as e:
        conexao.rollback()
        return False
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
    # Criação de tabela de usuários, se não existir
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            perfil VARCHAR(50) NOT NULL
        );
    """)
    # Criação de tabela de produtos, se não existir
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

# Chame esta função no início do seu script para garantir que as tabelas existam
if __name__ == '__main__':
    criar_tabelas()
