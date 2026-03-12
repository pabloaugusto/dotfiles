## Papel Especializado E Handoff

- criar o agente `ai-startup-governor`
- `display_name` sugerido: `Guardiao de Startup`
- antes de `ready_for_work`, so ele fala com o usuario
- ele pode emitir apenas mensagens de `startup_in_progress`,
  `startup_blocked`, `wip_decision_pending` ou `startup_ready`
- depois de `startup_ready`, o agente dono da rodada recebe o handoff formal e
  passa a responder operacionalmente
- o `Scrum Master` continua owner da auditoria de conformidade do chat
- o `Guardiao de Startup` nao substitui o dono da entrega nem o `Scrum Master`;
  ele protege a porta de entrada da sessao
