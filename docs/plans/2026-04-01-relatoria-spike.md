# Spike: Relatoria na Camara para Coherence

Date: 2026-04-01

## Objetivo

Avaliar se `relatoria` pode virar o proximo bloco oficial de `coherence` sem criar heuristica fragil nem duplicacao desnecessaria entre `mcp-brasil` e acesso direto a API da Camara.

## Achados

### O que ja esta resolvido

- `propositions_summary` por autoria ficou viavel com rigor porque a Camara oferece filtro estrutural por deputado autor
- o `mcp-brasil` local foi evoluido para suportar `id_deputado_autor`
- o Memoria Civica ja validou localmente esse fluxo no smoke test

### O que muda em relatoria

`Relatoria` nao aparece, nesta avaliacao, como um filtro estrutural simples equivalente a `idDeputadoAutor`.

A trilha mais provavel passa por:

1. listar eventos legislativos
2. consultar itens de pauta de eventos relevantes
3. identificar pareceres e metadados de relator
4. vincular o deputado relator a uma proposicao relacionada

Isso e mais indireto que autoria e depende mais de combinacao entre agenda, pauta e proposicoes.

### Situacao no mcp-brasil

Hoje o `mcp-brasil` expõe na Camara:

- deputados
- proposicoes
- tramitacao
- votacoes
- agenda legislativa
- comissoes

Mas nao expõe ainda:

- consulta de pauta de evento
- leitura estruturada de parecer/relator
- filtro por relator

Logo, `relatoria` nao esta a uma pequena mudanca de parametro como aconteceu com autoria.

## Trade-offs

### Opcao 1: subir relatoria no mcp-brasil

Vantagens:

- mantem a integracao da Camara centralizada
- evita arquitetura hibrida no Memoria Civica
- produz uma capacidade generica para o dominio parlamentar

Custos:

- escopo maior que o PR de autoria
- exige desenhar pelo menos uma nova tool ou um novo bloco de resposta
- maior risco de discussao de design no upstream

Leitura:

So vale se o recorte for pequeno e generico, por exemplo expor pauta de evento com metadados de relatoria, sem agregacao editorial.

### Opcao 2: resolver localmente no Memoria Civica

Vantagens:

- controle total de prazo
- permite experimentar o criterio de `relatoria` sem depender de review externo

Custos:

- cria duplicacao para a mesma fonte Camara
- aumenta manutencao
- pode gerar retrabalho se o `mcp-brasil` evoluir depois

Leitura:

Nao e a melhor opcao para agora. O custo arquitetural e maior do que o ganho imediato.

### Opcao 3: adiar relatoria e fortalecer o que ja entrou

Vantagens:

- reduz risco metodologico
- aproveita melhor autoria e votos nominais antes de abrir nova frente
- mantem a arquitetura limpa enquanto o PR upstream amadurece

Custos:

- posterga o terceiro bloco forte de `coherence`
- o produto evolui menos no curto prazo

Leitura:

E a opcao mais prudente se o objetivo for preservar clareza arquitetural.

## Recomendacao

Nao implementar `relatoria` agora.

Proximo passo recomendado:

1. esperar o desfecho do PR upstream de autoria
2. consolidar `propositions_summary` como parte estavel do fluxo
3. abrir um spike proprio para `pauta de eventos` no `mcp-brasil`
4. so depois decidir se existe um recorte generico e pequeno o suficiente para upstream

## Decisao pratica

Enquanto o PR de autoria esta em revisao, o melhor investimento local nao e `relatoria`.

As frentes com melhor relacao custo/beneficio sao:

- documentar o slice de `propositions_summary`
- alinhar stories/status AIOX com a nova validacao
- melhorar observabilidade e mensagens da trilha de `coherence`
- preparar a adocao limpa do PR upstream quando ele for aceito
