# Pesquisa de Arquitetura Modular Python

- Status: `recomendacao-aprovada-para-roadmap`
- Data-base: `2026-03-07`
- Escopo: modularizacao orientada a dominios, pacotes importaveis e possivel
  evolucao futura para microservicos

## Fontes pesquisadas

- PyPA sobre `src layout`:
  [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- `PEP 621` sobre metadata em [`pyproject.toml`](../../pyproject.toml):
  [PEP 621](https://peps.python.org/pep-0621/)
- `PEP 420` sobre namespace packages:
  [PEP 420](https://peps.python.org/pep-0420/)
- Martin Fowler sobre inicio por monolito modular:
  [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)

## Achados

### 1. O baseline correto e pacote importavel com `src layout`

Para portabilidade real entre projetos, a base nao deve crescer em scripts
soltos. O nucleo precisa existir como pacote Python importavel, isolado do
resto do repo e carregado por entrypoints finos.

### 2. [`pyproject.toml`](../../pyproject.toml) deve ser o contrato do pacote

Os modulos portaveis devem nascer com metadata, dependencias e entrypoints
declarados no [`pyproject.toml`](../../pyproject.toml), em vez de depender de
convencoes implicitas por repo.

### 3. Namespace package e ferramenta de expansao, nao requisito da v1

`PEP 420` e util quando a fabrica passar a distribuir dominios em multiplos
pacotes independentes. Para a v1, um pacote regular bem modularizado e mais
simples e menos arriscado.

### 4. Microservicos nao devem ser o ponto de partida

A recomendacao arquitetural mais segura para este piloto e comecar por um
monolito modular forte, com fronteiras de dominio duras e baixo acoplamento.
Extracao para microservicos deve acontecer apenas quando houver pressao real de
escala, deploy independente ou isolamento operacional.

## Recomendacao para este sistema

### V1

- adotar `modular monolith`
- organizar o nucleo Atlassian + control plane em pacotes por dominio
- manter [`../../scripts/`](../../scripts/) como wrappers CLI finos
- manter clients gerados isolados do dominio

### V2

- promover dominios estaveis para pacotes independentes dentro do monorepo
- permitir importacao seletiva por outros repos da fabrica
- introduzir namespace packages apenas se a distribuicao em multiplos pacotes
  realmente fizer sentido

### V3

- avaliar extracao seletiva para microservicos apenas em dominios que provarem
  necessidade operacional propria
- exemplos potenciais:
  - `migration-orchestrator`
  - `jira-sync-worker`
  - `confluence-publisher`

## Estrutura recomendada

```text
src/ai_control_plane/
  core/
    config/
    contracts/
    artifacts/
  domains/
    jira/
    confluence/
    migration/
    discovery/
  integrations/
    atlassian/
      generated/
      facades/
      auth/
      transport/
  application/
    apply_jira_schema.py
    seed_jira.py
    seed_confluence.py
    attach_migration_bundle.py
```

## Decisao pratica

- esta direcao entra no roadmap de maturidade do sistema
- nao e requisito da v1 bloquear a entrega atual
- todos os novos modulos Atlassian devem ser escritos ja pensando nessa
  fronteira portavel
