"""API GraphQL da rede social. Porta 8001 (GraphiQL em http://127.0.0.1:8001/graphql)."""
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

import service as s


#  tipos 
@strawberry.type
class Comentario:
    id: int
    usuario_id: int
    post_id: int
    texto: str
    criado_em: str


@strawberry.type
class Usuario:
    id: int
    nome: str
    email: str

    # Os campos abaixo só são buscados se o cliente pedir (essa é a graça do GraphQL)
    @strawberry.field
    def bio(self) -> str:
        return s.buscar_usuario(self.id)["bio"]

    @strawberry.field
    def total_seguidores(self) -> int:
        return s.buscar_usuario(self.id)["total_seguidores"]

    @strawberry.field
    def total_seguindo(self) -> int:
        return s.buscar_usuario(self.id)["total_seguindo"]

    @strawberry.field
    def posts(self) -> list["Post"]:
        return [_post(p) for p in s.posts_do_usuario(self.id)]

    @strawberry.field
    def seguidores(self) -> list["Usuario"]:
        return [_usuario(u) for u in s.seguidores_de(self.id)]

    @strawberry.field
    def seguindo(self) -> list["Usuario"]:
        return [_usuario(u) for u in s.seguindo_de(self.id)]

    @strawberry.field
    def feed(self) -> list["Post"]:
        return [_post(p) for p in s.feed_do_usuario(self.id)]


@strawberry.type
class Post:
    id: int
    autor_id: int
    texto: str
    criado_em: str

    @strawberry.field
    def autor(self) -> Usuario:
        return _usuario(s.buscar_usuario(self.autor_id))

    @strawberry.field
    def total_curtidas(self) -> int:
        return s.buscar_post(self.id)["total_curtidas"]

    @strawberry.field
    def comentarios(self) -> list[Comentario]:
        return [Comentario(**c) for c in s.buscar_post(self.id)["comentarios"]]


def _usuario(d):
    return Usuario(id=d["id"], nome=d["nome"], email=d["email"])


def _post(d):
    return Post(
        id=d["id"], autor_id=d["autor_id"], texto=d["texto"], criado_em=d["criado_em"]
    )


#  consultas 
@strawberry.type
class Query:
    @strawberry.field
    def usuario(self, id: int) -> Usuario:
        return _usuario(s.buscar_usuario(id))

    @strawberry.field
    def posts_do_usuario(self, usuario_id: int) -> list[Post]:
        return [_post(p) for p in s.posts_do_usuario(usuario_id)]

    @strawberry.field
    def post(self, id: int) -> Post:
        return _post(s.buscar_post(id))

    @strawberry.field
    def seguidores_de(self, id: int) -> list[Usuario]:
        return [_usuario(u) for u in s.seguidores_de(id)]

    @strawberry.field
    def seguindo_de(self, id: int) -> list[Usuario]:
        return [_usuario(u) for u in s.seguindo_de(id)]

    @strawberry.field
    def feed_do_usuario(self, usuario_id: int) -> list[Post]:
        return [_post(p) for p in s.feed_do_usuario(usuario_id)]


#  comandos 
@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_usuario(self, nome: str, email: str) -> Usuario:
        return _usuario(s.criar_usuario(nome, email))

    @strawberry.mutation
    def criar_post(self, usuario_id: int, texto: str) -> Post:
        return _post(s.criar_post(usuario_id, texto))

    @strawberry.mutation
    def comentar(self, usuario_id: int, post_id: int, texto: str) -> Comentario:
        return Comentario(**s.comentar(usuario_id, post_id, texto))

    @strawberry.mutation
    def curtir(self, usuario_id: int, post_id: int) -> Post:
        s.curtir(usuario_id, post_id)
        return _post(s.buscar_post(post_id))

    @strawberry.mutation
    def seguir(self, usuario_id: int, alvo_id: int) -> Usuario:
        s.seguir(usuario_id, alvo_id)
        return _usuario(s.buscar_usuario(alvo_id))


schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI(title="Rede Social - GraphQL")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)