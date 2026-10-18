# Atividade 02: APIs e protocolos

Nesta atividade eu expus o mesmo domínio, uma rede social simplificada (usuários, perfis, posts, comentários, curtidas e seguidores), em dois protocolos: REST e GraphQL. Cada um é um projeto separado, feito em Python, com o seu próprio banco SQLite.

- `rest-json/`: API REST em JSON, com FastAPI, na porta 8000.
- `graphql/`: API GraphQL, com FastAPI e Strawberry, na porta 8001.

Os dois têm os cinco comandos (`criar_usuario`, `criar_post`, `comentar`, `curtir` e `seguir`) e as consultas (`buscar_usuario`, `posts_do_usuario`, `buscar_post`, `seguidores_de` e `seguindo_de`, `feed_do_usuario`). O README de cada pasta tem um exemplo de requisição e de resposta, pronto para copiar, para cada operação.

## Como executar

Cada projeto roda sozinho, a partir da própria pasta. O passo a passo está no README de cada um (`rest-json/README.md` e `graphql/README.md`). Em resumo, precisa de Python 3.10 ou mais novo e, dentro da pasta do projeto:

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Depois, o REST pode ser testado em http://127.0.0.1:8000/docs e o GraphQL em http://127.0.0.1:8001/graphql. Os dois podem rodar ao mesmo tempo, porque usam portas diferentes.

## A diferença entre os dois

No REST, o servidor define o que cada endereço devolve. Para obter dados diferentes, o cliente acessa endereços diferentes (`/usuarios/1`, `/posts/1`, `/usuarios/1/feed`).

No GraphQL, existe um único endereço, `/graphql`, e o cliente descreve exatamente os dados que quer. O servidor devolve só aquilo.

Um exemplo com a mesma tela, o feed da Ana com o autor, as curtidas e os comentários de cada post:

- No REST, precisei de uma requisição para o feed, uma para cada post (para ver curtidas e comentários) e uma para o autor. Com 1 post foram 3 requisições, e cada post a mais soma mais uma.
- No GraphQL, foi uma query só, pedindo todos esses campos de uma vez (está no README do GraphQL).

Outra diferença está nos erros. No REST, curtir duas vezes responde com status 409, e só de olhar o status já se sabe que deu errado. No GraphQL, a resposta vem com status 200 e o erro aparece numa lista `errors` dentro do JSON.

Também há diferença no cache: no REST, cada `GET` tem a sua URL e é fácil de cachear. No GraphQL, tudo é `POST` no mesmo endereço, então é mais difícil.

## Comparação final

O REST foi mais simples de fazer: uma função por rota, e dá para testar com `curl` ou com o Swagger. O GraphQL deu mais trabalho, porque foi preciso definir os tipos e um resolver para cada campo.

Nos comandos (criar usuário, postar, comentar, curtir e seguir) achei os dois parecidos, e o REST ficou até mais claro por causa dos status HTTP. Nas consultas, principalmente no feed, o GraphQL se saiu melhor, porque esse domínio tem muitas relações ligadas entre si e ele busca tudo de uma vez.

Eu usaria REST em um app com poucas telas e dados simples, ou quando o cache for importante. Usaria GraphQL quando a tela juntar muitos dados relacionados, como o feed de uma rede social, ou quando telas diferentes precisarem de campos diferentes.

- O REST faz melhor: operações simples, fáceis de testar e com um status HTTP claro para cada resultado.
- O GraphQL faz melhor: buscar vários dados relacionados de uma vez, pedindo só o que a tela precisa.

## Limitações

No GraphQL, cada campo aninhado faz as suas próprias consultas ao banco, então um feed grande faria muitas consultas por trás (o problema N+1). Eu não resolvi isso porque o foco era comparar os protocolos. Também não coloquei login nem autenticação em nenhum dos dois.
