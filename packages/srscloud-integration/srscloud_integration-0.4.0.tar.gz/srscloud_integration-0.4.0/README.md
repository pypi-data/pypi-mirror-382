# SRSCloud Integration

Biblioteca para integração com SRSCloud, permitindo automação de processos com API.

## 🚀 Instalação

Para instalar a biblioteca, use:

```sh
pip install srscloud-integration
```

## 🔹 Uso Básico

Exemplo de uso básico da biblioteca:

```python
from srscloud_integration import SRS

srs = SRS(token="seu_token", maquina="minha_maquina", workflow="meu_workflow", tarefa="minha_tarefa")
srs.execucaoIniciar()
```

## 📌 Exemplo Prático

A biblioteca inclui um **arquivo de exemplo** chamado `exemplo_tarefa.py`, que demonstra um fluxo completo de uso, incluindo:
✅ Iniciar uma execução  
✅ Registrar logs  
✅ Finalizar o processo  

### 🔍 **Como encontrar o exemplo?**
Para localizar o código do **`exemplo_tarefa.py`**, use o comando:

```sh
python -c "import srscloud_integration; print(srscloud_integration.__file__)"
```

Isso mostrará o caminho onde a biblioteca foi instalada. Navegue até essa pasta para visualizar o código.

### 🚀 **Como executar o exemplo?**
Se deseja rodar o exemplo diretamente, utilize:

```sh
python -m srscloud_integration.exemplo_tarefa
```

Isso executará o script de exemplo, demonstrando a interação com a API SRSCloud.

## 📝 Documentação

Para mais informações, acesse o repositório oficial:  
🔗 [https://github.com/Automate-Brasil/srscloud-integration](https://github.com/Automate-Brasil/srscloud-integration)
```