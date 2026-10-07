# Instruções de uso — Simulador de rede de filas (T2)

Simulador de eventos discretos em Python 3 para **qualquer topologia de rede de
filas**. Lê um arquivo `.yml` no mesmo formato do simulador do Módulo 3 e
imprime, para cada fila, a distribuição de estados (tempo e probabilidade), o
número de perdas, a vazão observada e os **índices de desempenho** do M9:
população (N), vazão (D), utilização (U) e tempo de resposta (W).

## Requisitos

Python 3 e a biblioteca PyYAML:

    pip install pyyaml

## Como rodar

    python3 simulador.py modelos/oficina.yml
    python3 simulador.py modelos/oficina_melhorada.yml

Para salvar a saída em arquivo:

    python3 simulador.py modelos/oficina.yml > resultados/oficina_atual.txt

## Formato do `.yml`

O arquivo começa com a linha de marcação `!PARAMETERS` (exigida pelo simulador
do Módulo 3; aqui ela é apenas ignorada) e tem os blocos abaixo.

- `arrivals`: instante da primeira chegada externa de cada fila. Só as filas
  listadas aqui recebem clientes do exterior.
- `queues`: dados de cada fila.
  - `servers`: número de atendentes.
  - `capacity`: número máximo de clientes no sistema (em atendimento + em espera).
    Se não for informado, a fila é infinita.
  - `minArrival` e `maxArrival`: intervalo entre chegadas externas.
  - `minService` e `maxService`: tempo de atendimento.
- `network`: roteamento, com `source`, `target` e `probability`. A soma das
  probabilidades de uma fila não precisa dar 1: o que faltar sai da rede
  (exterior). Um `target` que não seja uma fila do modelo (p. ex. `EXTERIOR`)
  também conta como saída.
- `seeds` e `rndnumbersPerSeed`: geram os aleatórios automaticamente, um conjunto
  por semente, com `rndnumbersPerSeed` números cada. Se `seeds` for usado,
  `rndnumbers` é ignorado.
- `rndnumbers`: lista fixa de aleatórios entre 0 e 1, usada para testar.
- Os parâmetros `a`, `c` e `m` do gerador podem ser trocados (padrão
  25214903917, 11 e 2^48, os mesmos do simulador do Módulo 3).

## Como o simulador funciona

Os eventos são do tipo **chegada** e **saída**. Uma saída guarda o destino
sorteado quando o atendimento começou; se esse destino for outra fila, o cliente
entra nela (passagem), senão sai da rede. Ao iniciar um atendimento, o simulador
sorteia **primeiro o roteamento e depois o tempo de atendimento**. Os números vêm
de `U(a,b) = a + (b-a)*x`. O estado de uma fila é o número de clientes no sistema
(0 até a capacidade); uma chegada (externa ou por passagem) em fila cheia é
perdida. A cada evento todas as filas acumulam o tempo que passaram no estado
atual. A simulação para quando os números aleatórios acabam.

Quando há mais de uma semente, as sementes são executadas em sequência e os
resultados são **acumulados** (tempo global, tempos por estado, perdas e saídas).
O relatório mostra o tempo global somado e o tempo médio por simulação.

## Índices de desempenho

Para cada fila, com `E[S] = (minService + maxService)/2`, `MU = 1/E[S]` e
`Ns = Σ min(k, servers)·P(estado k)` (ocupação média dos servidores):

- População: `N = Σ k·P(estado k)`
- Vazão: `D = MU·Ns`
- Utilização: `U = Ns/servers = D/(servers·MU)`
- Tempo de resposta: `W = N/D` (Lei de Little)

O relatório também exibe a **vazão observada** (`saídas / tempo global`), que
deve ficar próxima da vazão calculada por `MU·Ns`.

## Saída

Para cada fila o relatório mostra a notação de Kendall, as chegadas e o
atendimento, chegadas externas, clientes atendidos, perdas, saídas, `E[S]`, `MU`,
os quatro índices de desempenho e uma linha por estado com o tempo acumulado e a
probabilidade. No fim aparece o tempo global da simulação.

## Verificação

O simulador é o mesmo validado no T1 contra o simulador de referência do Módulo 3
(`simulator.jar`): com a lista explícita de aleatórios do exemplo do Módulo 3, os
tempos por estado e o tempo global batem exatamente.
