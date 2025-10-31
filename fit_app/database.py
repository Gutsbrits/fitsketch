# database.py
import sqlite3

def inicializar_db():
    """Inicializa o banco de dados e cria a tabela se não existir."""
    conn = sqlite3.connect("fit.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data TEXT,
        exercicio TEXT,
        series INTEGER,
        repeticoes INTEGER,
        carga REAL,
        observacoes TEXT
    )
    """)
    conn.commit()
    return conn, cursor


def inserir_treino(dados):
    conn, cursor = inicializar_db()
    cursor.execute("""
        INSERT INTO treinos (nome, data, exercicio, series, repeticoes, carga, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, dados)
    conn.commit()
    conn.close()


def atualizar_treino(dados):
    conn, cursor = inicializar_db()
    cursor.execute("""
        UPDATE treinos SET nome=?, data=?, exercicio=?, series=?, repeticoes=?, carga=?, observacoes=?
        WHERE id=?
    """, dados)
    conn.commit()
    conn.close()


def excluir_treino(treino_id):
    conn, cursor = inicializar_db()
    cursor.execute("DELETE FROM treinos WHERE id=?", (treino_id,))
    conn.commit()
    conn.close()


def listar_treinos(filtros=None):
    conn, cursor = inicializar_db()
    sql = "SELECT * FROM treinos WHERE 1=1"
    valores = []

    if filtros:
        if filtros.get("nome"):
            sql += " AND nome LIKE ?"
            valores.append("%" + filtros["nome"] + "%")
        if filtros.get("data"):
            sql += " AND data LIKE ?"
            valores.append("%" + filtros["data"] + "%")
        if filtros.get("exercicio"):
            sql += " AND exercicio LIKE ?"
            valores.append("%" + filtros["exercicio"] + "%")

    sql += " ORDER BY id DESC"
    cursor.execute(sql, valores)
    registros = cursor.fetchall()
    conn.close()
    return registros
