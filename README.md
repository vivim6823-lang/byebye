# Cardápio da lanchonete

Aplicação Django para manter categorias e produtos pelo painel administrativo e disponibilizar o cardápio por uma API REST somente de leitura, criada com Django REST Framework, serializers, viewsets e router. Os dados ficam em SQLite por padrão.

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

## API

A API não exige autenticação e não permite alterações. Os serializers expõem apenas os campos públicos e representam a categoria do produto de forma aninhada. Os viewsets são registrados em um router; use o painel autenticado para cadastrar e atualizar os dados.

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/categories/` | Lista categorias ativas |
| `GET` | `/api/products/` | Lista produtos de categorias ativas |
| `GET` | `/api/products/{id}/` | Consulta um produto pelo identificador |

Exemplo de resposta de `/api/products/`:

```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "X-Burger",
      "description": "Hambúrguer, queijo e salada.",
      "price": "22.90",
      "is_available": true,
      "category": {
        "id": 1,
        "name": "Lanches"
      }
    }
  ]
}
```

Parâmetros opcionais de `/api/products/`:

- `category_id`: filtra pelo ID de uma categoria ativa.
- `available`: `true` ou `false`, para filtrar a disponibilidade.
- `q`: busca sem distinção entre maiúsculas e minúsculas no nome e na descrição.
- `page`: página solicitada (padrão `1`).
- `page_size`: resultados por página (padrão `50`, máximo `100`).

A resposta paginada contém `count`, `next`, `previous` e `results`; `next` e `previous` são números de página ou `null`. Parâmetros inválidos retornam HTTP `400`; um produto inexistente ou de categoria inativa retorna `404`. Endpoints que não sejam `GET` retornam `405`.

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
