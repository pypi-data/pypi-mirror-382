# mtcli-volume
  
Plugin para exibir o *Volume Profile* no terminal, com suporte a *acessibilidade total* para leitores de tela. Ideal para traders cegos, com baixa visão ou que preferem trabalhar no terminal.
  
## O que é?
  
O `mtcli-volume` integra-se ao [mtcli](https://github.com/vfranca/mtcli) e mostra a distribuição de volume por faixas de preço (Volume Profile), incluindo:
  
- *POC (Ponto de Controle)* — faixa com maior volume.
- *VA (Área de Valor)* — onde ocorre cerca de 70% do volume.
- *HVNs e LVNs* — regiões de alto/baixo volume.
- Saída 100% textual.
- Compatível com leitores como NVDA, Orca, VoiceOver.
  
---
  
Exemplo de uso
  
```bash
mt volume --symbol WINV25 --periods 566 --step 100
```
  
Saída típica:
  
```text
Volume Profile WINV25

 117400 |   2100 ██████████████████████
 117200 |    850 █████████
 117000 |    420 ████
 116800 |    120 █
 116600 |     60 

POC (Preço de Maior Volume): 117400
Área de Valor: 117200 a 117600
HVNs: [117400, 117200]
LVNs: [116600]
```
  
---
  
Modo acessível: sem barras
  
Use `--sem-barras` para desativar a visualização com caracteres de barra (`█`), ideal para leitores de tela:
  
```bash
mt volume --symbol WINV25 --sem-barras
```
  
  Saída:
  
```text
Volume Profile WINV25

 117400 |   2100
 117200 |    850
 117000 |    420
...

POC (Preço de Maior Volume): 117400
Área de Valor: 117200 a 117600
```
  
---
  
Exportar para CSV
  
```bash
mt volume --symbol WINV25 --exporta-csv
```
  
Cria um arquivo como:
  
```text
volume_profile_WINV25_20250914_1130.csv
```
  
---
  
## Instalação
  
```bash
pip install mtcli-volume
```
  
---
  
## Repositórios relacionados
  
- Plugin: [vfranca/mtcli-volume](https://github.com/vfranca/mtcli-volume)
- Base: [vfranca/mtcli](https://github.com/vfranca/mtcli)
- Exemplo: [vfranca/plugin-exemplo](https://github.com/vfranca/plugin-exemplo)
  
---
  
## Contribua
  
Sinta-se à vontade para abrir issues, pull requests, ou sugerir novas funcionalidades relacionadas à acessibilidade e análise técnica via terminal.
