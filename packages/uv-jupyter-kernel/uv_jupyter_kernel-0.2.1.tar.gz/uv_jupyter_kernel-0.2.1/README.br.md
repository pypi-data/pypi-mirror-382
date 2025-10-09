# uv-jupyter-kernel

Script para configurar kernels do Jupyter que utilizam o gerenciador de ambientes e dependências [uv](https://github.com/astral-sh/uv). Permite criar kernels isolados para diferentes versões do Python, facilitando o uso do Jupyter com ambientes controlados e reprodutíveis.

## Requisitos
- Algum cliente Jupyter (ex: extensão do VSCode)
- [uv](https://github.com/astral-sh/uv) instalado e disponível no PATH

## Uso

```bash
uvx uv-jupyter-kernel --versions 3.13 3.12
```

Por padrão, o script configura kernels para as versões 3.13 e 3.12 do Python. Você pode especificar outras versões passando-as como argumentos.

Isso irá criar (ou atualizar) arquivos de kernel em `~/.local/share/jupyter/kernels/uv-<versao>/kernel.json`, permitindo selecionar o kernel correspondente ao Python desejado dentro do Jupyter.

## O que o script faz?
- Localiza o executável do `uv` no sistema.
- Para cada versão de Python informada, cria um kernel Jupyter que:
  - Instala de forma efêmera o `ipykernel` e inicia o executor em sí.
  - Garante que o PATH do `uv` está disponível no ambiente do kernel.
  - Permite rodar cada notebook em um ambiente independente, efêmero e isolado.

## Vantagens
- A única coisa que precisa estar disponível inicialmente é o uv.
- Ambientes efêmeros: cada notebook tem o seu e pode instalar novas dependências com `uv pip install` e ao reiniciar o Jupyter o ambiente é resetado.
- Não precisa instalar o Jupyter no ambiente: menos chance de conflito de dependências.
- Cache compartilhado: cada coisa pode ser baixada só uma vez e depois reusada.

## Desvantagens
- Maior uso de disco se o seu sistema não suporta hardlinks (ex: Termux no Android) 