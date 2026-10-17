# CONTEXT_RULES — TaskAnalyzer

- Python 3.11+ e type hints em todas as funções.
- Aplicar SRP, PEP 8, docstrings e logging padrão.
- Tratar erros com exceções específicas e mensagens claras.
- Não usar bibliotecas externas não autorizadas (pytest apenas para testes).
- Não alterar os cenários para forçar aprovação.
- Não persistir dados, alterar assinatura pública ou inventar regras de negócio.
- Mudanças de escopo exigem aprovação humana; executar e revisar testes antes do merge.

Fonte: especificação SDD da Fase 1, seção 3.
