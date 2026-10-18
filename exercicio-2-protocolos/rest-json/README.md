# REST (JSON)

API REST da rede social, feita com **FastAPI**. Porta **8000**.

## Como executar (do zero)

Requer Python 3.10 ou superior. Dentro da pasta `rest-json/`:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

O servidor sobe em http://127.0.0.1:8000. A documentação interativa (Swagger), onde dá para testar cada rota pelo navegador, fica em http://127.0.0.1:8000/docs.

O banco é o arquivo `rede_social.db`, criado sozinho na pasta do projeto na primeira chamada. Os exemplos abaixo partem do banco **vazio**; para recomeçar, pare o servidor e apague o arquivo.

> Os `curl` abaixo funcionam em Linux, Mac e Git Bash. No PowerShell do Windows, use o Swagger em `/docs`.

## Rotas

| Operação | Método e rota | Sucesso |
|---|---|---|
| criar_usuario | `POST /usuarios` | 201 |
| criar_post | `POST /usuarios/{id}/posts` | 201 |
| comentar | `POST /posts/{id}/comentarios` | 201 |
| curtir | `POST /posts/{id}/curtidas` | 201 |
| seguir | `POST /usuarios/{id}/seguir` | 201 |
| buscar_usuario | `GET /usuarios/{id}` | 200 |
| posts_do_usuario | `GET /usuarios/{id}/posts` | 200 |
| buscar_post | `GET /posts/{id}` | 200 |
| seguidores_de | `GET /usuarios/{id}/seguidores` | 200 |
| seguindo_de | `GET /usuarios/{id}/seguindo` | 200 |
| feed_do_usuario | `GET /usuarios/{id}/feed` | 200 |

Erros: `404` (não encontrado), `400` (dado inválido, ex.: seguir a si mesmo), `409` (conflito, ex.: curtir duas vezes ou email repetido) e `422` (corpo malformado, validado pelo FastAPI). Os erros de negócio vêm como `{"erro": "..."}`.

## Exemplos (copiáveis, executar na ordem)

Os valores de `criado_em` são só ilustrativos; no seu teste aparece a data e hora reais.

### 1. criar_usuario (Ana)

```bash
curl -X POST http://127.0.0.1:8000/usuarios -H "Content-Type: application/json" -d '{"nome": "Ana", "email": "ana@email.com"}'
```

Resposta (HTTP 201):

```json
{"id": 1, "nome": "Ana", "email": "ana@email.com"}
```

### 2. criar_usuario (Bruno)

```bash
curl -X POST http://127.0.0.1:8000/usuarios -H "Content-Type: application/json" -d '{"nome": "Valter", "email": "valter@email.com"}'
```

Resposta (HTTP 201):

```json
{"id": 2, "nome": "Bruno", "email": "bruno@email.com"}
```

### 3. criar_post (Bruno posta)

```bash
curl -X POST http://127.0.0.1:8000/usuarios/2/posts -H "Content-Type: application/json" -d '{"texto": "Meu primeiro post"}'
```

Resposta (HTTP 201):

```json
{"id": 1, "autor_id": 2, "texto": "Meu primeiro post", "criado_em": "2026-10-18 14:32:05"}
```

### 4. criar_post (segundo post do Bruno)

```bash
curl -X POST http://127.0.0.1:8000/usuarios/2/posts -H "Content-Type: application/json" -d '{"texto": "Segundo post do Bruno"}'
```

Resposta (HTTP 201):

```json
{"id": 2, "autor_id": 2, "texto": "Segundo post do Bruno", "criado_em": "2026-10-18 14:32:20"}
```

### 5. comentar (Ana comenta o post 1)

```bash
curl -X POST http://127.0.0.1:8000/posts/1/comentarios -H "Content-Type: application/json" -d '{"usuario_id": 1, "texto": "Bem-vindo!"}'
```

Resposta (HTTP 201):

```json
{"id": 1, "usuario_id": 1, "post_id": 1, "texto": "Bem-vindo!", "criado_em": "2026-10-18 14:33:01"}
```

### 6. curtir (Ana curte o post 1)

```bash
curl -X POST http://127.0.0.1:8000/posts/1/curtidas -H "Content-Type: application/json" -d '{"usuario_id": 1}'
```

Resposta (HTTP 201):

```json
{"usuario_id": 1, "post_id": 1, "total_curtidas": 1}
```

### 7. seguir (Ana segue Bruno)

```bash
curl -X POST http://127.0.0.1:8000/usuarios/1/seguir -H "Content-Type: application/json" -d '{"alvo_id": 2}'
```

Resposta (HTTP 201):

```json
{"seguidor_id": 1, "seguido_id": 2}
```

### 8. buscar_usuario

```bash
curl http://127.0.0.1:8000/usuarios/2
```

Resposta (HTTP 200):

```json
{"id": 2, "nome": "Bruno", "email": "bruno@email.com", "bio": "", "total_seguidores": 1, "total_seguindo": 0}
```

### 9. posts_do_usuario

```bash
curl http://127.0.0.1:8000/usuarios/2/posts
```

Resposta (HTTP 200):

```json
[
  {"id": 2, "autor_id": 2, "texto": "Segundo post do Bruno", "criado_em": "2026-10-18 14:32:20"},
  {"id": 1, "autor_id": 2, "texto": "Meu primeiro post", "criado_em": "2026-10-18 14:32:05"}
]
```

### 10. buscar_post

```bash
curl http://127.0.0.1:8000/posts/1
```

Resposta (HTTP 200):

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

### 11. seguidores_de

```bash
curl http://127.0.0.1:8000/usuarios/2/seguidores
```

Resposta (HTTP 200):

```json
[{"id": 1, "nome": "Ana", "email": "ana@email.com"}]
```

### 12. seguindo_de

```bash
curl http://127.0.0.1:8000/usuarios/1/seguindo
```

Resposta (HTTP 200):

```json
[{"id": 2, "nome": "Bruno", "email": "bruno@email.com"}]
```

### 13. feed_do_usuario

```bash
curl http://127.0.0.1:8000/usuarios/1/feed
```

Resposta (HTTP 200):

```json
[
  {"id": 2, "autor_id": 2, "texto": "Segundo post do Bruno", "criado_em": "2026-10-18 14:32:20"},
  {"id": 1, "autor_id": 2, "texto": "Meu primeiro post", "criado_em": "2026-10-18 14:32:05"}
]
```

### 14. Erro: curtir duas vezes

```bash
curl -X POST http://127.0.0.1:8000/posts/1/curtidas -H "Content-Type: application/json" -d '{"usuario_id": 1}'
```

Resposta (HTTP 409):

```json
{"erro": "usuário já curtiu este post"}
```

### 15. Erro: usuário inexistente

```bash
curl http://127.0.0.1:8000/usuarios/999
```

Resposta (HTTP 404):

```json
{"erro": "usuário 999 não encontrado"}
```

## O que o REST faz melhor que o GraphQL, neste domínio

Cada operação é uma URL com um verbo e um status HTTP próprio, então dá para testar com um `curl` simples, cachear os `GET` (perfil, post) e entender o resultado sem nenhuma ferramenta extra.