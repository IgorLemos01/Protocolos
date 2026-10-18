# GraphQL

API GraphQL da rede social, feita com **FastAPI + Strawberry**. Porta **8001**, com um único endpoint: `/graphql`.

## Como executar (do zero)

Requer Python 3.10 ou superior. Dentro da pasta `graphql/`:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

O servidor sobe em http://127.0.0.1:8001/graphql. Abrindo essa URL no navegador aparece o **GraphiQL**, um editor onde você escreve a query à esquerda e vê a resposta à direita (botão ▶ para executar).

O banco é o arquivo `rede_social.db`, criado sozinho na pasta do projeto na primeira chamada. Os exemplos abaixo partem do banco **vazio**; para recomeçar, pare o servidor e apague o arquivo.

Para usar sem o GraphiQL, toda operação é um `POST /graphql` com o corpo `{"query": "..."}`:

```bash
curl -X POST http://127.0.0.1:8001/graphql -H "Content-Type: application/json" -d '{"query": "{ usuario(id: 1) { nome } }"}'
```

> Esse `curl` funciona em Linux, Mac e Git Bash. No PowerShell do Windows, use o GraphiQL.

## Operações

| Operação | Tipo | Nome no schema |
|---|---|---|
| criar_usuario | Mutation | `criarUsuario(nome, email)` |
| criar_post | Mutation | `criarPost(usuarioId, texto)` |
| comentar | Mutation | `comentar(usuarioId, postId, texto)` |
| curtir | Mutation | `curtir(usuarioId, postId)` |
| seguir | Mutation | `seguir(usuarioId, alvoId)` |
| buscar_usuario | Query | `usuario(id)` |
| posts_do_usuario | Query | `postsDoUsuario(usuarioId)` |
| buscar_post | Query | `post(id)` |
| seguidores_de | Query | `seguidoresDe(id)` |
| seguindo_de | Query | `seguindoDe(id)` |
| feed_do_usuario | Query | `feedDoUsuario(usuarioId)` |

Os tipos `Usuario` e `Post` são conectados: `Usuario` tem `posts`, `seguidores`, `seguindo` e `feed`; `Post` tem `autor`, `totalCurtidas` e `comentarios`. Por isso uma query pode navegar por tudo (veja o exemplo 14).

Erros de negócio (usuário inexistente, curtida repetida etc.) voltam com HTTP 200 e uma lista `errors` na resposta, que é o comportamento padrão do GraphQL.

## Exemplos (copiáveis, executar na ordem)

Os valores de `criadoEm` são só ilustrativos.

### 1. criar_usuario (Ana)

```graphql
mutation {
  criarUsuario(nome: "Ana", email: "ana@email.com") { id nome email }
}
```

```json
{"data": {"criarUsuario": {"id": 1, "nome": "Ana", "email": "ana@email.com"}}}
```

### 2. criar_usuario (Bruno)

```graphql
mutation {
  criarUsuario(nome: "Bruno", email: "bruno@email.com") { id nome email }
}
```

```json
{"data": {"criarUsuario": {"id": 2, "nome": "Bruno", "email": "bruno@email.com"}}}
```

### 3. criar_post

```graphql
mutation {
  criarPost(usuarioId: 2, texto: "Meu primeiro post") { id autorId texto criadoEm }
}
```

```json
{"data": {"criarPost": {"id": 1, "autorId": 2, "texto": "Meu primeiro post", "criadoEm": "2026-10-18 14:40:05"}}}
```

### 4. criar_post (segundo)

```graphql
mutation {
  criarPost(usuarioId: 2, texto: "Segundo post do Bruno") { id texto }
}
```

```json
{"data": {"criarPost": {"id": 2, "texto": "Segundo post do Bruno"}}}
```

### 5. comentar

```graphql
mutation {
  comentar(usuarioId: 1, postId: 1, texto: "Bem-vindo!") { id usuarioId postId texto }
}
```

```json
{"data": {"comentar": {"id": 1, "usuarioId": 1, "postId": 1, "texto": "Bem-vindo!"}}}
```

### 6. curtir

```graphql
mutation {
  curtir(usuarioId: 1, postId: 1) { id totalCurtidas }
}
```

```json
{"data": {"curtir": {"id": 1, "totalCurtidas": 1}}}
```

### 7. seguir

```graphql
mutation {
  seguir(usuarioId: 1, alvoId: 2) { id nome totalSeguidores }
}
```

```json
{"data": {"seguir": {"id": 2, "nome": "Bruno", "totalSeguidores": 1}}}
```

### 8. buscar_usuario

```graphql
{
  usuario(id: 2) { id nome email bio totalSeguidores totalSeguindo }
}
```

```json
{"data": {"usuario": {"id": 2, "nome": "Bruno", "email": "bruno@email.com", "bio": "", "totalSeguidores": 1, "totalSeguindo": 0}}}
```

### 9. posts_do_usuario

```graphql
{
  postsDoUsuario(usuarioId: 2) { id texto criadoEm }
}
```

```json
{"data": {"postsDoUsuario": [
  {"id": 2, "texto": "Segundo post do Bruno", "criadoEm": "2026-10-18 14:40:20"},
  {"id": 1, "texto": "Meu primeiro post", "criadoEm": "2026-10-18 14:40:05"}
]}}
```

### 10. buscar_post

```graphql
{
  post(id: 1) { id texto totalCurtidas comentarios { usuarioId texto } }
}
```

```json
{"data": {"post": {"id": 1, "texto": "Meu primeiro post", "totalCurtidas": 1, "comentarios": [{"usuarioId": 1, "texto": "Bem-vindo!"}]}}}
```

### 11. seguidores_de

```graphql
{
  seguidoresDe(id: 2) { id nome }
}
```

```json
{"data": {"seguidoresDe": [{"id": 1, "nome": "Ana"}]}}
```

### 12. seguindo_de

```graphql
{
  seguindoDe(id: 1) { id nome }
}
```

```json
{"data": {"seguindoDe": [{"id": 2, "nome": "Bruno"}]}}
```

### 13. feed_do_usuario

```graphql
{
  feedDoUsuario(usuarioId: 1) { id texto autor { nome } }
}
```

```json
{"data": {"feedDoUsuario": [
  {"id": 2, "texto": "Segundo post do Bruno", "autor": {"nome": "Bruno"}},
  {"id": 1, "texto": "Meu primeiro post", "autor": {"nome": "Bruno"}}
]}}
```

### 14. Bônus: tudo da Ana em UMA requisição

```graphql
{
  usuario(id: 1) {
    nome
    seguindo { nome }
    feed {
      texto
      autor { nome }
      totalCurtidas
      comentarios { texto }
    }
  }
}
```

```json
{"data": {"usuario": {
  "nome": "Ana",
  "seguindo": [{"nome": "Bruno"}],
  "feed": [
    {"texto": "Segundo post do Bruno", "autor": {"nome": "Bruno"}, "totalCurtidas": 0, "comentarios": []},
    {"texto": "Meu primeiro post", "autor": {"nome": "Bruno"}, "totalCurtidas": 1, "comentarios": [{"texto": "Bem-vindo!"}]}
  ]
}}}
```

### 15. Erro: curtir duas vezes

```graphql
mutation {
  curtir(usuarioId: 1, postId: 1) { id }
}
```

```json
{"data": null, "errors": [{"message": "usuário já curtiu este post", "locations": [{"line": 2, "column": 3}], "path": ["curtir"]}]}
```

## O que o GraphQL faz melhor que o REST, neste domínio

O cliente escolhe os campos e navega pelas relações (usuário, feed, autor, curtidas e comentários) em uma única requisição, o que evita várias idas ao servidor para montar um feed.