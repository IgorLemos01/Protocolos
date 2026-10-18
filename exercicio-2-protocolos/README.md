# Atividade 02: APIs e protocolos

Nesta atividade eu expus o mesmo domínio, uma rede social simplificada (usuários, perfis, posts, comentários, curtidas e seguidores), em dois protocolos diferentes: **REST** e **GraphQL**. Cada um é um projeto separado, feito em Python, com o seu próprio banco SQLite.

| Pasta | Protocolo | Tecnologia | Porta |
|---|---|---|---|
| [`rest-json/`](rest-json/README.md) | REST (JSON) | FastAPI | 8000 |
| [`graphql/`](graphql/README.md) | GraphQL | FastAPI e Strawberry | 8001 |

Os dois têm os cinco comandos (`criar_usuario`, `criar_post`, `comentar`, `curtir` e `seguir`) e as consultas (`buscar_usuario`, `posts_do_usuario`, `buscar_post`, `seguidores_de` e `seguindo_de`, `feed_do_usuario`). O README de cada pasta traz um exemplo de requisição e de resposta para cada operação, pronto para copiar.

## Como executar

Cada projeto roda sozinho, a partir da própria pasta. O passo a passo completo está no README de cada um. Em resumo, precisa de Python 3.10 ou mais novo e, dentro da pasta `rest-json/` ou `graphql/`:

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Depois, o REST pode ser testado em http://127.0.0.1:8000/docs e o GraphQL em http://127.0.0.1:8001/graphql. Os dois podem rodar ao mesmo tempo, porque usam portas diferentes.

## A diferença entre os dois, em uma frase

- No **REST**, o servidor define o que cada endereço devolve. Para obter dados diferentes, o cliente acessa endereços diferentes.
- No **GraphQL**, existe um único endereço e o cliente descreve exatamente os dados que quer. O servidor devolve só aquilo.

## A diferença na prática

### 1. Mesma operação, criar um usuário

REST: o verbo e o endereço dizem o que fazer, e o corpo traz os dados.

```bash
curl -X POST http://127.0.0.1:8000/usuarios -H "Content-Type: application/json" -d '{"nome": "Ana", "email": "ana@email.com"}'
```

```json
{"id": 1, "nome": "Ana", "email": "ana@email.com"}
```

GraphQL: o endereço é sempre `/graphql`, e o que fazer vem escrito na própria query. Eu escolho quais campos voltam.

```graphql
mutation {
  criarUsuario(nome: "Ana", email: "ana@email.com") { id nome }
}
```

```json
{"data": {"criarUsuario": {"id": 1, "nome": "Ana"}}}
```

No REST o `email` voltou porque o servidor decidiu assim. No GraphQL ele não voltou porque eu não pedi.

### 2. Mesma tela, o feed da Ana

Imagine uma tela que mostra o feed da Ana, com o nome do autor, as curtidas e os comentários de cada post.

**No REST, precisei de 4 requisições** (no meu exemplo, o feed tinha 2 posts do mesmo autor):

```
GET /usuarios/1/feed        -> os posts (só id, autor_id, texto e data)
GET /posts/1                -> curtidas e comentários do post 1
GET /posts/2                -> curtidas e comentários do post 2
GET /usuarios/2             -> o nome do autor
```

Com mais posts e mais autores, o número de requisições cresce.

**No GraphQL, foi 1 requisição:**

```graphql
{
  usuario(id: 1) {
    nome
    feed {
      texto
      autor { nome }
      totalCurtidas
      comentarios { texto }
    }
  }
}
```

### 3. Mesmo erro, curtir duas vezes

- **REST:** a resposta vem com status **409** e o corpo `{"erro": "usuário já curtiu este post"}`. Basta olhar o status para saber que deu errado.
- **GraphQL:** a resposta vem com status **200** e uma lista `errors` dentro do JSON. É preciso ler o conteúdo para saber que deu errado.

## Comparação final

| | REST | GraphQL |
|---|---|---|
| Endereços | Uma URL para cada recurso e operação | Um só, `/graphql` |
| Quem decide o que vem na resposta | O servidor | O cliente |
| Montar o feed completo | 4 requisições no meu exemplo | 1 requisição |
| Campos que sobram ou faltam | Pode acontecer (traz demais ou de menos) | Vem só o que foi pedido |
| Erros | Status HTTP (404, 400, 409) | Status 200, com o erro numa lista `errors` |
| Cache | Fácil, cada `GET` tem a sua URL | Mais difícil, tudo é `POST` no mesmo endereço |
| Testar à mão | `curl` ou Swagger (`/docs`) | GraphiQL (`/graphql`) |
| Esforço para implementar | Uma função por rota | Definir os tipos e um resolver por campo |
| Documentação | Gerada pelo FastAPI (Swagger) | O próprio schema serve de documentação |

## Quando eu usaria cada um

**REST**, quando o app tem poucas telas e dados simples, ou quando o cache importa. Cada operação é um endereço com um status claro, é fácil de testar com `curl` e de entender.

**GraphQL**, quando a tela junta muitos dados relacionados, como o feed de uma rede social, ou quando telas diferentes precisam de campos diferentes. O cliente pede só o que precisa, em uma requisição.

## O que cada um faz melhor nesse domínio

- **REST:** operações simples, fáceis de testar e de cachear, com um status HTTP claro para cada resultado.
- **GraphQL:** buscar vários dados relacionados de uma vez (como o feed), pedindo só o que a tela precisa.

## Observações

- Nos comandos (criar usuário, postar, comentar, curtir e seguir) eu achei os dois parecidos. O REST ficou até mais claro por causa dos status HTTP.
- No GraphQL, cada campo aninhado faz as suas próprias consultas ao banco, então um feed grande faria muitas consultas por trás (o conhecido problema N+1). Eu não resolvi isso porque o foco era comparar os protocolos.
- Não coloquei login nem autenticação em nenhum dos dois.