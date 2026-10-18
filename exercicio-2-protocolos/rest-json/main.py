"""API REST (JSON) da rede social. Porta 8000."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import service as s

app = FastAPI(title="Rede Social - REST")


# ---------- erros de negócio -> status HTTP ----------
def _erro(status):
    async def handler(request, exc):
        return JSONResponse(status_code=status, content={"erro": str(exc)})
    return handler


app.add_exception_handler(s.NaoEncontrado, _erro(404))
app.add_exception_handler(s.Invalido, _erro(400))
app.add_exception_handler(s.Conflito, _erro(409))


# ---------- corpos de requisição ----------
class NovoUsuario(BaseModel):
    nome: str
    email: str


class NovoPost(BaseModel):
    texto: str


class NovoComentario(BaseModel):
    usuario_id: int
    texto: str


class NovaCurtida(BaseModel):
    usuario_id: int


class NovoSeguir(BaseModel):
    alvo_id: int


# ---------- comandos (escrita) ----------
@app.post("/usuarios", status_code=201)
def criar_usuario(body: NovoUsuario):
    return s.criar_usuario(body.nome, body.email)


@app.post("/usuarios/{usuario_id}/posts", status_code=201)
def criar_post(usuario_id: int, body: NovoPost):
    return s.criar_post(usuario_id, body.texto)


@app.post("/posts/{post_id}/comentarios", status_code=201)
def comentar(post_id: int, body: NovoComentario):
    return s.comentar(body.usuario_id, post_id, body.texto)


@app.post("/posts/{post_id}/curtidas", status_code=201)
def curtir(post_id: int, body: NovaCurtida):
    return s.curtir(body.usuario_id, post_id)


@app.post("/usuarios/{usuario_id}/seguir", status_code=201)
def seguir(usuario_id: int, body: NovoSeguir):
    return s.seguir(usuario_id, body.alvo_id)


# ---------- consultas (leitura) ----------
@app.get("/usuarios/{usuario_id}")
def buscar_usuario(usuario_id: int):
    return s.buscar_usuario(usuario_id)


@app.get("/usuarios/{usuario_id}/posts")
def posts_do_usuario(usuario_id: int):
    return s.posts_do_usuario(usuario_id)


@app.get("/posts/{post_id}")
def buscar_post(post_id: int):
    return s.buscar_post(post_id)


@app.get("/usuarios/{usuario_id}/seguidores")
def seguidores_de(usuario_id: int):
    return s.seguidores_de(usuario_id)


@app.get("/usuarios/{usuario_id}/seguindo")
def seguindo_de(usuario_id: int):
    return s.seguindo_de(usuario_id)


@app.get("/usuarios/{usuario_id}/feed")
def feed_do_usuario(usuario_id: int):
    return s.feed_do_usuario(usuario_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)