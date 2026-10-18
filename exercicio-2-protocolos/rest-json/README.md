# API REST (JSON)

A rede social exposta como API REST, feita em Python com FastAPI. Os dados ficam em um banco SQLite (um arquivo na própria pasta). O servidor roda na porta 8000.

## Como rodar

Precisa de Python 3.10 ou mais novo. Dentro da pasta `rest-json/`:

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Quando aparecer `Uvicorn running on http://127.0.0.1:8000`, o servidor está no ar.

## Como testar

O FastAPI gera uma página para testar as rotas pelo navegador: http://127.0.0.1:8000/docs. Em cada rota, clique em "Try it out", preencha e clique em "Execute".

Também dá para usar os `curl` dos exemplos abaixo (funcionam no Linux, no Mac e no Git Bash; no PowerShell do Windows use o Swagger).

O arquivo `rede_social.db` é criado sozinho na primeira requisição. Os exemplos começam com o banco vazio e devem ser rodados na ordem, porque os ids dependem disso. Para recomeçar, pare o servidor e apague o `rede_social.db`.

## Erros

Os erros usam o status HTTP, e o corpo vem como `{"erro": "mensagem"}`:

- 404: usuário ou post não encontrado
- 400: dado inválido (por exemplo, seguir a si mesmo)
- 409: conflito (curtir duas vezes, seguir duas vezes, email repetido)
- 422: corpo da requisição malformado (validação do próprio FastAPI)

## Comandos

### criar_usuario (POST /usuarios)

```bash
curl -X POST http://127.0.0.1:8000/usuarios -H "Content-Type: application/json" -d '{"nome": "Ana", "email": "ana@email.com"}'
```

Resposta (201):

```json
{"id": 1, "nome": "Ana", "email": "ana@email.com"}
```

Crie também o Bruno (vai ser o id 2):

```bash
curl -X POST http://127.0.0.1:8000/usuarios -H "Content-Type: application/json" -d '{"nome": "Bruno", "email": "bruno@email.com"}'
```

### criar_post (POST /usuarios/{id}/posts)

O Bruno posta:

```bash
curl -X POST http://127.0.0.1:8000/usuarios/2/posts -H "Content-Type: application/json" -d '{"texto": "Meu primeiro post"}'
```

Resposta (201):

```json
{"id": 1, "autor_id": 2, "texto": "Meu primeiro post", "criado_em": "2026-10-18 14:32:05"}
```

Crie um segundo post, que vai ser usado nos exemplos de consulta:

```bash
curl -X POST http://127.0.0.1:8000/usuarios/2/posts -H "Content-Type: application/json" -d '{"texto": "Segundo post do Bruno"}'
```

### comentar (POST /posts/{id}/comentarios)

A Ana comenta o post 1:

```bash
curl -X POST http://127.0.0.1:8000/posts/1/comentarios -H "Content-Type: application/json" -d '{"usuario_id": 1, "texto": "Bem-vindo!"}'
```

Resposta (201):

```json
{"id": 1, "usuario_id": 1, "post_id": 1, "texto": "Bem-vindo!", "criado_em": "2026-10-18 14:33:01"}
```

### curtir (POST /posts/{id}/curtidas)

A Ana curte o post 1:

```bash
curl -X POST http://127.0.0.1:8000/posts/1/curtidas -H "Content-Type: application/json" -d '{"usuario_id": 1}'
```

Resposta (201):

```json
{"usuario_id": 1, "post_id": 1, "total_curtidas": 1}
```

Se rodar de novo, volta erro 409: `{"erro": "usuário já curtiu este post"}`.

### seguir (POST /usuarios/{id}/seguir)

A Ana segue o Bruno:

```bash
curl -X POST http://127.0.0.1:8000/usuarios/1/seguir -H "Content-Type: application/json" -d '{"alvo_id": 2}'
```

Resposta (201):

```json
{"seguidor_id": 1, "seguido_id": 2}
```

## Consultas

### buscar_usuario (GET /usuarios/{id})

```bash
curl http://127.0.0.1:8000/usuarios/2
```

Resposta (200):

```json
{"id": 2, "nome": "Bruno", "email": "bruno@email.com", "bio": "", "total_seguidores": 1, "total_seguindo": 0}
```

Se o usuário não existe (por exemplo `/usuarios/999`), volta 404: `{"erro": "usuário 999 não encontrado"}`.

### posts_do_usuario (GET /usuarios/{id}/posts)

```bash
curl http://127.0.0.1:8000/usuarios/2/posts
```

Resposta (200), do mais novo para o mais antigo:

```json
[
  {"id": 2, "autor_id": 2, "texto": "Segundo post do Bruno", "criado_em": "2026-10-18 14:32:20"},
  {"id": 1, "autor_id": 2, "texto": "Meu primeiro post", "criado_em": "2026-10-18 14:32:05"}
]
```

### buscar_post (GET /posts/{id})

```bash
curl http://127.0.0.1:8000/posts/1
```

Resposta (200):

```json
{
  "id": 1,
  "autor_id": 2,
  "texto": "Meu primeiro post",
  "criado_em": "2026-10-18 14:32:05",
  "total_curtidas": 1,
  "comentarios": [
    {"id": 1, "usuario_id": 1, "post_id": 1, "texto": "Bem-vindo!", "criado_em": "2026-10-18 14:33:01"}
  ]
}
```

### seguidores_de (GET /usuarios/{id}/seguidores)

```bash
curl http://127.0.0.1:8000/usuarios/2/seguidores
```

Resposta (200):

```json
[{"id": 1, "nome": "Ana", "email": "ana@email.com"}]
```

### seguindo_de (GET /usuarios/{id}/seguindo)

```bash
curl http://127.0.0.1:8000/usuarios/1/seguindo
```

Resposta (200):

```json
[{"id": 2, "nome": "Bruno", "email": "bruno@email.com"}]
```

### feed_do_usuario (GET /usuarios/{id}/feed)

Os posts de quem o usuário segue, do mais novo para o mais antigo:

```bash
curl http://127.0.0.1:8000/usuarios/1/feed
```

Resposta (200):

```json
[
  {"id": 2, "autor_id": 2, "texto": "Segundo post do Bruno", "criado_em": "2026-10-18 14:32:20"},
  {"id": 1, "autor_id": 2, "texto": "Meu primeiro post", "criado_em": "2026-10-18 14:32:05"}
]
```

Repare que o feed só traz os posts. O nome do autor, as curtidas e os comentários precisam de outras requisições (`GET /usuarios/{id}` e `GET /posts/{id}`).

## O que o REST faz melhor que o GraphQL nesse domínio

Cada operação é um endereço com um verbo e um status HTTP próprio, então é fácil de testar, de entender o resultado e de cachear os `GET`.
