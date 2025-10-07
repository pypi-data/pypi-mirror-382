# mtcli-atr
  
Plugin do `mtcli` para calcular o indicador *ATR (Average True Range)* via linha de comando, usando dados do MetaTrader 5.
  
---
  
## Requisitos
  
- Python ≥ 3.10  
- MetaTrader 5 instalado e configurado  
- Conta ativa em corretora compatível com MT5  
  
---
  
## Instalação
  
Instale o plugin via pip:
  
```bash
pip install mtcli-atr
```
  
---
  
## Uso
  
```bash
mt atr --symbol IBOV --period D1 --bars 14
```
  
Parâmetros
  
| Parâmetro          | Descrição                                              | Padrão |
|--------------------|---------------------------------------------------------|--------|
| `--symbol`, `-s`    | Símbolo do ativo                                       | IBOV   |
| `--period`, `-p` | Timeframe das barras (ex: M1, H1, D1)                | D1     |
| `--bars`, `-b`  | Quantidade de barras para o cálculo do ATR                         | 14     |
  
---
  
Exemplo completo
  
```bash
mt atr -s PETR4 -p H1 -b 10
```
  
Exemplo de saída esperada:
    
```text
ATR(10) de PETR4 no timeframe H1: 123.45
```
  
---
  
## Contribuindo
  
Para instruções de desenvolvimento, estrutura de código e testes, veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md).
  
---
  
Licença
  
Este projeto está licenciado sob a GNU General Public License v3.0.  
Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
