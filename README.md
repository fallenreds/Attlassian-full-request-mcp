# Sidis Atlassian MCP Server

FastMCP server exposing **30 tools** for full Jira + Confluence access.

## Запуск локально

```bash
pip install -r requirements.txt
python server.py
# → http://localhost:8080/mcp
```

## Подключение в Claude / любом MCP-клиенте

```json
{
  "mcpServers": {
    "sidis-atlassian": {
      "type": "streamable-http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

## Деплой на Prefect

```bash
pip install prefect
prefect deploy --all
```

После деплоя сервер доступен через:
`horizon.prefect.io/sidis-group/servers`

## Инструменты

### Jira (16 tools)
| Tool | Описание |
|------|---------|
| `jira_get_issue` | Получить issue по ключу (SL-4, ADK-119) |
| `jira_search` | Поиск по JQL |
| `jira_create_issue` | Создать задачу |
| `jira_update_issue` | Обновить поля задачи |
| `jira_transition_issue` | Сменить статус |
| `jira_get_transitions` | Получить доступные статусы |
| `jira_add_comment` | Добавить комментарий |
| `jira_delete_issue` | Удалить задачу |
| `jira_get_projects` | Список всех проектов |
| `jira_get_issue_types` | Типы задач проекта |
| `jira_assign_issue` | Назначить исполнителя |
| `jira_get_user` | Данные пользователя |
| `jira_search_users` | Поиск пользователей |
| `jira_get_comments` | Комментарии к задаче |
| `jira_create_link` | Связать две задачи |
| `jira_get_sprint_issues` | Задачи спринта |

### Confluence (14 tools)
| Tool | Описание |
|------|---------|
| `confluence_get_spaces` | Список пространств |
| `confluence_create_space` | Создать пространство |
| `confluence_get_page` | Получить страницу по ID |
| `confluence_search` | Поиск по CQL |
| `confluence_create_page` | Создать страницу (plain text) |
| `confluence_create_page_html` | Создать страницу (HTML) |
| `confluence_update_page` | Обновить страницу |
| `confluence_delete_page` | Удалить страницу |
| `confluence_get_children` | Дочерние страницы |
| `confluence_add_comment` | Добавить комментарий |
| `confluence_move_page` | Переместить страницу |
| `confluence_get_space_homepage` | Homepage пространства |
| `confluence_get_pages_in_space` | Страницы пространства |
| `confluence_attach_file_url` | Прикрепить файл по URL |

## Конфигурация

Параметры в `server.py`:
- `ATLASSIAN_BASE` — URL инстанса
- `EMAIL` — логин
- `API_TOKEN` — токен Atlassian
- `CLOUD_ID` — ID облака Sidis Group
