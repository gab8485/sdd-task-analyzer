# Contrato SDD — TaskAnalyzer

Fonte: Especificação SDD da Fase 1, seções 1 e 2.

`analyze_tasks(tasks, reference_date=None)` recebe lista de dicionários com:
- `id` (int ou str, único), `title` (str não vazia), `status` (`pending` ou `completed`)
- `created_at` e `due_date` (date/datetime; due_date >= created_at)
- `completed_at` (obrigatório para completed; >= created_at; None para pending)

Retorna `total_tasks`, `completed_tasks`, `pending_tasks`, `overdue_tasks`,
`completion_rate`, `overdue_rate`, `average_completion_hours`.

- Atraso: completed_at > due_date para concluídas; due_date < reference_date para pendentes.
- Taxas: quantidade / total * 100, arredondadas a 2 casas.
- Média: horas entre criação e conclusão das concluídas, 2 casas.
- Lista vazia e ausência de concluídas: taxas/médias 0.0.
- Datas inválidas e status inválido: ValueError (TaskValidationError é subtipo).

## Extensões explícitas solicitadas na Fase 2

- `TaskValidationError(ValueError)` para erros de validação.
- Campo opcional `priority` (texto não vazio), sem vocabulário imposto, pois a Fase 1 não o define.
- `average_completion_hours_by_priority`: dicionário com médias das prioridades presentes em tarefas concluídas; vazio quando nenhuma prioridade está presente.

**Revisão humana necessária:** o formato da prioridade e a chave adicional são decisões de compatibilização com a Fase 2, não requisitos originais da Fase 1.
