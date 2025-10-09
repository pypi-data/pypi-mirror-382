# Agents Upstream (Python)

[![PyPI version](https://img.shields.io/pypi/v/agents-upstream.svg)](https://pypi.org/project/agents-upstream/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/agents-upstream.svg)](https://pypi.org/project/agents-upstream/)

Sistema de análise de pesquisa com agentes especializados de IA para Product Discovery.

> **Nota:** Este é o pacote Python. Também disponível como [pacote Node.js/npm](https://www.npmjs.com/package/agents-upstream).

## 🚀 Instalação Rápida

> 📖 **Para instalação detalhada, consulte:** [QUICK_INSTALL.md](QUICK_INSTALL.md)

### 🎯 Método Recomendado - Instalador Inteligente

**Sempre instala no PATH do usuário (sem precisar de admin):**

```bash
# Download e instalação em um comando
curl -sSL https://raw.githubusercontent.com/marcelusfernandes/agents-upstream/main/python-package/install.py | python3

# Ou baixe primeiro:
wget https://raw.githubusercontent.com/marcelusfernandes/agents-upstream/main/python-package/install.py
python3 install.py          # Instala no usuário (padrão)
python3 install.py --pipx   # Usa pipx (ainda melhor)
python3 install.py -g       # Instala globalmente (se precisar)
```

### Via pipx (alternativa recomendada)

```bash
pipx run agents-upstream
# ou
pipx install agents-upstream
```

### Via pip manual

```bash
# Recomendado: Sempre use --user para evitar problemas de PATH
pip install --user agents-upstream
agents-upstream

# Ou instalação global (pode precisar de sudo/admin)
pip install agents-upstream
agents-upstream
```

> **✨ Configuração Automática de PATH**
>
> Se você instalar sem privilégios de administrador (usando `pip install --user`), o pacote **detecta automaticamente** se o PATH precisa ser configurado e oferece configurar para você:
>
> ```
> ⚠️  ATENÇÃO: Configuração de PATH necessária
> 
> Opções:
>   1. Configurar automaticamente (recomendado) ✨
>   2. Pular e usar 'pipx run agents-upstream'
>   3. Configurar manualmente depois
> ```
>
> **Configurar PATH depois:**
> ```bash
> # Se você pulou a configuração, pode configurar depois com:
> agents-upstream --setup-path
> 
> # Ou use python diretamente:
> python -m agents_upstream.cli --setup-path
> ```
>
> O pacote configura automaticamente para:
> - **Linux/Mac:** Adiciona `~/.local/bin` ao seu `.bashrc` ou `.zshrc`
> - **Windows:** Adiciona Scripts ao PATH do usuário (sem precisar de admin)

### Via pip (instalação em ambiente virtual)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install agents-upstream
agents-upstream
```

Isso criará toda a estrutura de pastas, templates e agentes de IA no diretório atual.

## 📦 O que está incluído?

- **9 Agentes Especializados de IA** para análise de problema e solução
- **17+ Templates profissionais** para análise estratégica
- **Sistema de workflow automatizado** com validação de qualidade
- **Documentação completa** com exemplos e melhores práticas

## 🎯 O que o sistema faz?

Transforma semanas de análise estratégica em horas, mantendo supervisão e validação humana:

- **Analisa entrevistas** e dados de pesquisa de usuários
- **Identifica automaticamente** problemas-chave, oportunidades e insights estratégicos
- **Gera análises completas** de pain points até recomendações de solução
- **Produz relatórios** prontos para executivos e roadmaps de implementação

## 📋 Requisitos

- **Python 3.8 ou superior**
- **Cursor AI** ou editor compatível com Cursor Rules

## 🔧 Como usar

### 1. Instalar

```bash
pipx run agents-upstream
```

### 2. Preparar materiais

- Coloque arquivos de entrevista em `0-documentation/0b-Interviews/`
- Atualize `0-documentation/0a-projectdocs/context.md` com objetivos do negócio

### 3. Iniciar workflow

No Cursor AI, digite:
```
start workflow
```

O sistema progride automaticamente pelos Agentes 0-5 (análise de problema) e depois Agentes 6-8 (desenvolvimento de solução).

## 📂 Estrutura criada

```
├── 0-documentation/          # Contexto do projeto e materiais fonte
│   ├── 0a-projectdocs/       # Documentação de contexto
│   └── 0b-Interviews/        # Arquivos de entrevista
├── _output-structure/        # Templates e guias de formatação
│   ├── problem-space/        # Templates de análise de problema
│   └── solution-space/       # Templates de desenvolvimento de solução
└── .cursor/                  # Agentes de IA e regras de workflow
    └── rules/
        ├── problem-space/    # Agentes 0-5
        └── solution-space/   # Agentes 6-8
```

## 🤖 Agentes Incluídos

### Problem Space (Agentes 0-5)
- **Agent 0:** Product & Service Design Specialist
- **Agent 1:** Qualitative Research Specialist
- **Agent 2:** Pain Point Analysis Specialist
- **Agent 3:** As-Is Journey Mapper
- **Agent 4:** Journey Consolidation Specialist
- **Agent 5:** Strategic Report Generator

### Solution Space (Agentes 6-8)
- **Agent 6:** Strategic Analysis Specialist
- **Agent 7:** Process Optimization Specialist
- **Agent 8:** Communication Specialist

## 📊 Entregáveis

### Pacote de Análise de Problema
- Declaração estratégica de problema
- Análise de pain points
- Mapeamento de jornada do estado atual
- Relatório abrangente de problema

### Pacote de Ideação de Solução
- Oportunidades estratégicas com ROI
- Roadmap de implementação
- Avaliação de automação
- Apresentação executiva
- Plano de gestão de mudança

## 🛠️ Desenvolvimento

### Instalação local para desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/marcelusfernandes/agents-upstream.git
cd agents-upstream/python-package

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# IMPORTANTE: Instale dependências de build/publicação
pip install build twine

# Instale em modo editável
pip install -e .

# Teste
agents-upstream
```

### Build Automatizado

O pacote Python **sincroniza automaticamente** com o repositório principal durante o build!

```bash
# Build completo (sincroniza templates + build)
python build_package.py

# Ou use o Makefile (recomendado)
make build

# Outros comandos úteis
make help          # Ver todos os comandos
make clean         # Limpar artefatos
make sync          # Apenas sincronizar templates
make test          # Testar instalação
make dev           # Instalar modo desenvolvimento
```

### ⚡ Vantagens do Build Automatizado

- ✅ **Uma única fonte de verdade:** Templates sempre sincronizados com `../template/`
- ✅ **Zero manutenção duplicada:** Não precisa copiar manualmente
- ✅ **Sempre atualizado:** Build garante templates mais recentes
- ✅ **Simples:** Um comando faz tudo

### Publicação

```bash
# Publicar no TestPyPI (teste)
make publish-test

# Publicar no PyPI (produção)
make publish

# Ou manualmente:
python build_package.py
python -m twine upload --repository testpypi dist/*  # TestPyPI
python -m twine upload dist/*                        # PyPI
```

## 🆚 Python vs Node.js

Ambas as versões oferecem a mesma funcionalidade. Escolha baseado no seu ambiente:

| Característica | Python (pipx) | Node.js (npx) |
|----------------|---------------|---------------|
| **Execução sem instalação** | ✅ `pipx run` | ✅ `npx` |
| **Templates incluídos** | ✅ Idênticos | ✅ Idênticos |
| **Agentes de IA** | ✅ Idênticos | ✅ Idênticos |
| **Telemetria** | ❌ Não | ✅ Opcional |
| **Dependências** | Nenhuma | posthog-node, chalk, etc |

**Recomendação:**
- Use **Python** se você trabalha principalmente com Python
- Use **Node.js** se você trabalha com desenvolvimento web/frontend

## 📝 Licença

MIT

## 🤝 Contribuindo

Contribuições são bem-vindas! Este é um sistema em evolução projetado para melhoria contínua.

### Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 🐛 Troubleshooting

**Problema: Comando não encontrado após instalação?**

**Solução Automática (Recomendado):**
```bash
# Configure PATH automaticamente em um comando
agents-upstream --setup-path

# Ou se isso não funcionar, use Python diretamente:
python -m agents_upstream.cli --setup-path
```

**Alternativas:**
- Use `pipx run agents-upstream` (não requer configuração de PATH)
- Consulte o [Guia de Troubleshooting PATH](PATH_TROUBLESHOOTING.md) para configuração manual detalhada

## 📧 Suporte

- **Documentação:** Consulte a documentação completa incluída após a instalação
- **Troubleshooting PATH:** [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md)
- **Issues:** [GitHub Issues](https://github.com/marcelusfernandes/agents-upstream/issues)
- **Discussões:** [GitHub Discussions](https://github.com/marcelusfernandes/agents-upstream/discussions)

---

**Permite que equipes de produto pensem estrategicamente sem sacrificar velocidade.**

