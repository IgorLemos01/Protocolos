# API GraphQL

A rede social exposta como API GraphQL, feita em Python com FastAPI e Strawberry. Os dados ficam em um banco SQLite (um arquivo na própria pasta). O servidor roda na porta 8001 e tem um único endereço: `/graphql`.

## Como rodar

Precisa de Python 3.10 ou mais novo. Dentro da pasta `graphql/`:

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Quando aparecer `Uvicorn running on http://127.0.0.1:8001`, o servidor está no ar.

## Como testar

Abra http://127.0.0.1:8001/graphql no navegador. Essa página é o GraphiQL: escreva a query do lado esquerdo, clique no botão de play e a resposta aparece do lado direito.

Sem o GraphiQL, toda operação é um `POST /graphql` com a query dentro de um JSON:

```bash
curl -X POST http://127.0.0.1:8001/graphql -H "Content-Type: application/json" -d '{"query": "{ usuario(id: 1) { nome } }"}'
```

(Esse `curl` funciona no Linux, no Mac e no Git Bash; no PowerShell do Windows use o GraphiQL.)

O arquivo `rede_social.db` é criado sozinho na primeira requisição. Os exemplos começam com o banco vazio e devem ser rodados na ordem, porque os ids dependem disso. Para recomeçar, pare o servidor e apague o `rede_social.db`.

## Como funciona

Comandos (que alteram dados) são `mutation`. Consultas (que só leem) são `query`, e dá para escrever só `{ ... }`. Em ambos, eu escolho quais campos quero na resposta.

Os tipos são ligados entre si: um `Usuario` tem `posts`, `seguidores`, `seguindo` e `feed`, e um `Post` tem `autor`, `totalCurtidas` e `comentarios`. Por isso uma query só pode andar por tudo isso.

Erros de regra (usuário que não existe, curtir duas vezes) voltam com status HTTP 200 e uma lista `errors` dentro do JSON. É o comportamento normal do GraphQL.

## Comandos

### criar_usuario (mutation criarUsuario)

```graphql
mutation {
  criarUsuario(nome: "Ana", email: "ana@email.com") { id nome email }
}
```

Resposta:

```json
{"data": {"criarUsuario": {"id": 1, "nome": "Ana", "email": "ana@email.com"}}}
```

Crie também o Bruno (vai ser o id 2):

```graphql
mutation {
  criarUsuario(nome: "Bruno", email: "bruno@email.com") { id nome email }
}
```

### criar_post (mutation criarPost)

O Bruno posta:

```graphql
mutation {
  criarPost(usuarioId: 2, texto: "Meu primeiro post") { id autorId texto criadoEm }
}
```

Resposta:

```json
{"data": {"criarPost": {"id": 1, "autorId": 2, "texto": "Meu primeiro post", "criadoEm": "2026-10-18 14:40:05"}}}
```

Crie um segundo post, que vai ser usado nos exemplos de consulta:

```graphql
mutation {
  criarPost(usuarioId: 2, texto: "Segundo post do Bruno") { id texto }
}
```

### comentar (mutation comentar)

A Ana comenta o post 1:

```graphql
mutation {
  comentar(usuarioId: 1, postId: 1, texto: "Bem-vindo!") { id usuarioId postId texto }
}
```

Resposta:

```json
{"data": {"comentar": {"id": 1, "usuarioId": 1, "postId": 1, "texto": "Bem-vindo!"}}}
```

### curtir (mutation curtir)

A Ana curte o post 1:

```graphql
mutation {
  curtir(usuarioId: 1, postId: 1) { id totalCurtidas }
}
```

Resposta:

```json
{"data": {"curtir": {"id": 1, "totalCurtidas": 1}}}
```

Se rodar de novo, volta um erro dentro de `errors`:

```json
{"data": null, "errors": [{"message": "usuário já curtiu este post", "locations": [{"line": 2, "column": 3}], "path": ["curtir"]}]}
```

### seguir (mutation seguir)

A Ana segue o Bruno (a resposta é o usuário que foi seguido):

```graphql
mutation {
  seguir(usuarioId: 1, alvoId: 2) { id nome totalSeguidores }
}
```

Resposta:

```json
{"data": {"seguir": {"id": 2, "nome": "Bruno", "totalSeguidores": 1}}}
```

## Consultas

### buscar_usuario (usuario)

```graphql
{
  usuario(id: 2) { id nome email bio totalSeguidores totalSeguindo }
}
```

Resposta:

```json
{"data": {"usuario": {"id": 2, "nome": "Bruno", "email": "bruno@email.com", "bio": "", "totalSeguidores": 1, "totalSeguindo": 0}}}
```

### posts_do_usuario (postsDoUsuario)

```graphql
{
  postsDoUsuario(usuarioId: 2) { id texto criadoEm }
}
```

Resposta, do mais novo para o mais antigo:

```json
{"data": {"postsDoUsuario": [
  {"id": 2, "texto": "Segundo post do Bruno", "criadoEm": "2026-10-18 14:40:20"},
  {"id": 1, "texto": "Meu primeiro post", "criadoEm": "2026-10-18 14:40:05"}
]}}
```

### buscar_post (post)

```graphql
{
  post(id: 1) { id texto totalCurtidas comentarios { usuarioId texto } }
}
```

Resposta:

```json
{"data": {"post": {"id": 1, "texto": "Meu primeiro post", "totalCurtidas": 1, "comentarios": [{"usuarioId": 1, "texto": "Bem-vindo!"}]}}}
```

### seguidores_de (seguidoresDe)

```graphql
{
  seguidoresDe(id: 2) { id nome }
}
```

Resposta:

```json
{"data": {"seguidoresDe": [{"id": 1, "nome": "Ana"}]}}
```

### seguindo_de (seguindoDe)

```graphql
{
  seguindoDe(id: 1) { id nome }
}
```

Resposta:

```json
{"data": {"seguindoDe": [{"id": 2, "nome": "Bruno"}]}}
```

### feed_do_usuario (feedDoUsuario)

Os posts de quem o usuário segue, do mais novo para o mais antigo:

```graphql
{
  feedDoUsuario(usuarioId: 1) { id texto autor { nome } }
}
```

Resposta:

```json
{"data": {"feedDoUsuario": [
  {"id": 2, "texto": "Segundo post do Bruno", "autor": {"nome": "Bruno"}},
  {"id": 1, "texto": "Meu primeiro post", "autor": {"nome": "Bruno"}}
]}}
```

## Extra: tudo numa requisição só

Aqui aparece a principal diferença para o REST. Numa única query vêm quem a Ana segue e o feed dela, com o autor, as curtidas e os comentários de cada post:

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

Resposta:

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

## O que o GraphQL faz melhor que o REST nesse domínio

Ele monta o feed, com autor, curtidas e comentários de cada post, numa requisição só, trazendo apenas os campos que a tela precisa.
