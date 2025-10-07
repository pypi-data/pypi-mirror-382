# mtcli-risco
    
![Testes](https://github.com/vfranca/mtcli-risco/actions/workflows/tests.yml/badge.svg)
  
Plugin para controle de risco diário integrado ao mtcli. Bloqueia automaticamente o envio de ordens caso o limite de prejuízo do dia seja ultrapassado.
    
---
  
## Instalação
  
Instale via pip (com mtcli já instalado):
  
```bash
pip install mtcli-risco
```
  
---
  
## Requisitos
  
- Python 3.10+
- MetaTrader 5 instalado e configurado
- Conta de negociação conectada no MT5
- mtcli instalado e funcionando
  
---
  
## Como usar
  
Executar o comando:
  
```bash
mt risco
```
  
Exemplo com limite personalizado:
  
```bash
mt risco --limite -300
```
  
Isso bloqueará novas ordens quando o lucro total do dia (realizado + em aberto) for menor ou igual a -300.
  
---
  
📁 Arquivo de estado
  
O estado do risco diário é salvo no arquivo:
  
```bash
bloqueio_risco.json
```
  
Exemplo de conteúdo:
  
```json
{
  "data": "2025-09-20",
  "bloqueado": true
}
```
  
Esse arquivo é reavaliado a cada novo dia. O bloqueio se aplica apenas ao dia corrente.
  
---
  
## Lógica
  
1. Consulta as negociações realizadas no dia (buy/sell).
2. Soma os lucros/prejuízos dessas operações.
3. Adiciona o lucro/prejuízo da posição atual em aberto.
4. Se o total for menor ou igual ao limite definido, bloqueia novas ordens.
  
---
  
## Rodar testes
  
Execute os testes com:
  
```bash
pytest tests/
```
  
---
  
## Desenvolvimento
  
Clone e instale em modo editável:
  
```bash
git clone https://github.com/seuuser/mtcli-risco.git
cd mtcli-risco
pip install -e .
```
  
