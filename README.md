# Cardápio da lanchonete

Projeto Django com o app `cardapio`, painel administrativo e API REST de categorias e produtos, construída com Django REST Framework. A categoria (`Categoria`) tem nome obrigatório e único (`nome`, até 100 caracteres) e descrição opcional (`descricao`). O produto (`Produto`) tem nome obrigatório (`nome`, até 150 caracteres), descrição opcional (`descricao`), preço não negativo (`preco`), disponibilidade ativada por padrão (`disponivel`) e uma relação protegida `categoria` com `related_name="produtos"`. Os dados ficam em SQLite por padrão.

## Requisitos

- Python 3.10 ou superior
- pip

## Instalação e execução

No PowerShell, na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` antes de continuar: defina `DJANGO_SECRET_KEY` e substitua `ADMIN_PASSWORD` por uma senha forte. Depois, inicialize o banco e crie o administrador:

```powershell
python manage.py migrate
python manage.py bootstrap_admin
python manage.py runserver
```

Abra `http://127.0.0.1:8000/` para a página inicial, que oferece links para o painel e a API. Para gerenciar o cardápio, entre em `http://127.0.0.1:8000/admin/` com `ADMIN_USERNAME` e `ADMIN_PASSWORD` do `.env`. O Django Admin tem cabeçalho próprio, busca e filtros para as listas, edição rápida de disponibilidade e preço e timestamps de produto somente para leitura. Use **Categorias** e **Produtos** para manter o cardápio. Uma categoria com produtos associados não pode ser removida; remova ou reassocie os produtos primeiro.

Para criar ou atualizar o administrador novamente, execute `python manage.py bootstrap_admin`. O comando aplica a senha configurada no ambiente ao usuário indicado. Não use credenciais de exemplo em produção.

## API REST

Os endpoints de categorias e produtos oferecem CRUD completo. Leituras são públicas; operações de escrita exigem autenticação por token ou sessão.

| Método | Endpoint | Descrição |
|---|---|---|
| `GET`, `POST` | `/api/categorias/` | Lista e cria categorias |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/categorias/{id}/` | Consulta, atualiza e exclui uma categoria |
| `GET` | `/api/categorias/{id}/produtos/` | Lista os produtos da categoria |
| `GET`, `POST` | `/api/produtos/` | Lista e cria produtos |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/produtos/{id}/` | Consulta, atualiza e exclui um produto |
| `POST` | `/api/token/` | Obtém um token usando usuário e senha |
| `GET` | `/api/schema/` | Esquema OpenAPI |
| `GET` | `/api/docs/` | Documentação interativa Swagger |

Para criar ou atualizar dados, envie `Authorization: Token <token>`. O preço é validado no serializer e não pode ser negativo. A resposta dos produtos inclui `categoria_nome`.

Filtros e busca:

- `/api/produtos/?disponivel=true` ou `false` filtra pela disponibilidade.
- `/api/produtos/?search=burger` busca pelo nome, sem distinção entre maiúsculas e minúsculas.
- As listagens são paginadas com 50 resultados por página; use `?page=2` para avançar.

Exemplo de solicitação de token:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/token/ `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"sua-senha"}'
```

Use o valor retornado no cabeçalho `Authorization: Token ...` das solicitações de escrita.

## Configuração

As configurações podem ser definidas como variáveis de ambiente ou no `.env` local:

| Variável | Descrição |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta obrigatória do Django |
| `DJANGO_DEBUG` | Ativa o modo de desenvolvimento (`true` por padrão) |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos separados por vírgula |
| `ADMIN_USERNAME` | Usuário administrador criado por `bootstrap_admin` |
| `ADMIN_PASSWORD` | Senha aplicada pelo comando de bootstrap |
| `ADMIN_EMAIL` | E-mail opcional do administrador |

Em produção, defina `DJANGO_DEBUG=false`, configure `DJANGO_ALLOWED_HOSTS`, use uma chave e senha fortes e sirva a aplicação por HTTPS. O SQLite é adequado para começar; avalie um banco gerenciado antes de aumentar o volume ou operar múltiplas instâncias.

## Testes

```powershell
python manage.py test
```
