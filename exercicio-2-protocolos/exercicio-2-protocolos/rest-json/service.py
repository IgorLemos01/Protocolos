"""Regras de negócio da rede social.

Nenhuma linha aqui sabe o que é HTTP ou JSON: o main.py só chama estas funções.
"""
import sqlite3

from db import conectar


class ErroDominio(Exception):
    """Base dos erros de negócio."""


class NaoEncontrado(ErroDominio):
    pass


class Invalido(ErroDominio):
    pass


class Conflito(ErroDominio):
    pass


# ---------- helpers ----------

def _texto_obrigatorio(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise Invalido(f"'{campo}' é obrigatório")
    return valor.strip()


def _exige_usuario(con, usuario_id):
    row = con.execute("SELECT * FROM usuario WHERE id = ?", (usuario_id,)).fetchone()
    if row is None:
        raise NaoEncontrado(f"usuário {usuario_id} não encontrado")
    return row


def _exige_post(con, post_id):
    row = con.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
    if row is None:
        raise NaoEncontrado(f"post {post_id} não encontrado")
    return row


def _post_dict(row):
    return {
        "id": row["id"],
        "autor_id": row["autor_id"],
        "texto": row["texto"],
        "criado_em": row["criado_em"],
    }


# ---------- comandos ----------

def criar_usuario(nome, email):
    nome = _texto_obrigatorio(nome, "nome")
    email = _texto_obrigatorio(email, "email")
    if "@" not in email:
        raise Invalido("'email' inválido")
    with conectar() as con:
        try:
            cur = con.execute(
                "INSERT INTO usuario (nome, email) VALUES (?, ?)", (nome, email)
            )
        except sqlite3.IntegrityError:
            raise Conflito(f"já existe um usuário com o email {email}")
        uid = cur.lastrowid
        con.execute("INSERT INTO perfil (usuario_id) VALUES (?)", (uid,))
    return {"id": uid, "nome": nome, "email": email}


def criar_post(usuario_id, texto):
    texto = _texto_obrigatorio(texto, "texto")
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        cur = con.execute(
            "INSERT INTO post (autor_id, texto) VALUES (?, ?)", (usuario_id, texto)
        )
        row = con.execute("SELECT * FROM post WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _post_dict(row)


def comentar(usuario_id, post_id, texto):
    texto = _texto_obrigatorio(texto, "texto")
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        _exige_post(con, post_id)
        cur = con.execute(
            "INSERT INTO comentario (usuario_id, post_id, texto) VALUES (?, ?, ?)",
            (usuario_id, post_id, texto),
        )
        row = con.execute(
            "SELECT * FROM comentario WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return dict(row)


def curtir(usuario_id, post_id):
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        _exige_post(con, post_id)
        try:
            con.execute(
                "INSERT INTO curtida (usuario_id, post_id) VALUES (?, ?)",
                (usuario_id, post_id),
            )
        except sqlite3.IntegrityError:
            raise Conflito("usuário já curtiu este post")
        total = con.execute(
            "SELECT COUNT(*) FROM curtida WHERE post_id = ?", (post_id,)
        ).fetchone()[0]
    return {"usuario_id": usuario_id, "post_id": post_id, "total_curtidas": total}


def seguir(usuario_id, alvo_id):
    if usuario_id == alvo_id:
        raise Invalido("um usuário não pode seguir a si mesmo")
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        _exige_usuario(con, alvo_id)
        try:
            con.execute(
                "INSERT INTO seguidor (seguidor_id, seguido_id) VALUES (?, ?)",
                (usuario_id, alvo_id),
            )
        except sqlite3.IntegrityError:
            raise Conflito("usuário já segue este alvo")
    return {"seguidor_id": usuario_id, "seguido_id": alvo_id}


# ---------- consultas ----------

def buscar_usuario(usuario_id):
    with conectar() as con:
        u = _exige_usuario(con, usuario_id)
        perfil = con.execute(
            "SELECT bio FROM perfil WHERE usuario_id = ?", (usuario_id,)
        ).fetchone()
        n_seguidores = con.execute(
            "SELECT COUNT(*) FROM seguidor WHERE seguido_id = ?", (usuario_id,)
        ).fetchone()[0]
        n_seguindo = con.execute(
            "SELECT COUNT(*) FROM seguidor WHERE seguidor_id = ?", (usuario_id,)
        ).fetchone()[0]
    return {
        "id": u["id"],
        "nome": u["nome"],
        "email": u["email"],
        "bio": perfil["bio"] if perfil else "",
        "total_seguidores": n_seguidores,
        "total_seguindo": n_seguindo,
    }


def posts_do_usuario(usuario_id):
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        rows = con.execute(
            "SELECT * FROM post WHERE autor_id = ? ORDER BY criado_em DESC, id DESC",
            (usuario_id,),
        ).fetchall()
    return [_post_dict(r) for r in rows]


def buscar_post(post_id):
    with conectar() as con:
        p = _exige_post(con, post_id)
        comentarios = con.execute(
            "SELECT * FROM comentario WHERE post_id = ? ORDER BY criado_em, id",
            (post_id,),
        ).fetchall()
        total = con.execute(
            "SELECT COUNT(*) FROM curtida WHERE post_id = ?", (post_id,)
        ).fetchone()[0]
    d = _post_dict(p)
    d["total_curtidas"] = total
    d["comentarios"] = [dict(c) for c in comentarios]
    return d


def seguidores_de(usuario_id):
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        rows = con.execute(
            """SELECT u.id, u.nome, u.email FROM seguidor s
               JOIN usuario u ON u.id = s.seguidor_id
               WHERE s.seguido_id = ? ORDER BY u.id""",
            (usuario_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def seguindo_de(usuario_id):
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        rows = con.execute(
            """SELECT u.id, u.nome, u.email FROM seguidor s
               JOIN usuario u ON u.id = s.seguido_id
               WHERE s.seguidor_id = ? ORDER BY u.id""",
            (usuario_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def feed_do_usuario(usuario_id):
    """Posts de quem o usuário segue, do mais recente para o mais antigo."""
    with conectar() as con:
        _exige_usuario(con, usuario_id)
        rows = con.execute(
            """SELECT p.* FROM post p
               JOIN seguidor s ON s.seguido_id = p.autor_id
               WHERE s.seguidor_id = ?
               ORDER BY p.criado_em DESC, p.id DESC""",
            (usuario_id,),
        ).fetchall()
    return [_post_dict(r) for r in rows]