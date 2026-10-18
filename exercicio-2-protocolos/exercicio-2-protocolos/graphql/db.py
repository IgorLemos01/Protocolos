"""Banco SQLite do projeto GraphQL."""
import os
import sqlite3

# O banco fica na mesma pasta deste arquivo, de onde quer que o servidor seja iniciado.
_PASTA = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("REDE_DB", os.path.join(_PASTA, "rede_social.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuario (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- 1:1 com usuario
CREATE TABLE IF NOT EXISTS perfil (
    usuario_id INTEGER PRIMARY KEY REFERENCES usuario(id),
    bio        TEXT NOT NULL DEFAULT ''
);

-- 1:N (autor)
CREATE TABLE IF NOT EXISTS post (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    autor_id  INTEGER NOT NULL REFERENCES usuario(id),
    texto     TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- N:M com atributo (texto)
CREATE TABLE IF NOT EXISTS comentario (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    post_id    INTEGER NOT NULL REFERENCES post(id),
    texto      TEXT NOT NULL,
    criado_em  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- N:M puro
CREATE TABLE IF NOT EXISTS curtida (
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    post_id    INTEGER NOT NULL REFERENCES post(id),
    criado_em  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, post_id)
);

-- N:M auto-relacionamento (segue)
CREATE TABLE IF NOT EXISTS seguidor (
    seguidor_id INTEGER NOT NULL REFERENCES usuario(id),
    seguido_id  INTEGER NOT NULL REFERENCES usuario(id),
    criado_em   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (seguidor_id, seguido_id),
    CHECK (seguidor_id != seguido_id)
);
"""


def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row            # permite ler colunas pelo nome
    con.execute("PRAGMA foreign_keys = ON")  # o SQLite não confere FK sem isso
    con.executescript(SCHEMA)
    return con