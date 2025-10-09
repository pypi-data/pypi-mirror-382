# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [1.4.0] - 2025-10-08

### 🎉 Adicionado (MAJOR)
- **Instalador Inteligente (`install.py`)** - Script que SEMPRE instala no PATH do usuário por padrão
  - **Por padrão**: `pip install --user` (sem precisar de admin)
  - **Com `-g`**: Permite instalação global se necessário
  - **Com `--pipx`**: Instala usando pipx automaticamente
  - Detecta e configura PATH automaticamente após instalação
  - Interface interativa com feedback visual
  
- **Configuração Automática de PATH** - O pacote detecta e oferece configurar PATH
  - Detecta automaticamente quando PATH não está configurado
  - Oferece configuração automática durante a instalação
  - Detecta sistema operacional (Windows/Mac/Linux) e shell (bash/zsh/fish)
  - Novo comando `agents-upstream --setup-path` para configurar a qualquer momento
  - Suporte total para instalação sem privilégios de administrador

### Melhorado
- **Experiência do Usuário**: Usuários não precisam mais configurar PATH manualmente
- **Documentação**: README e guias atualizados com instruções de configuração automática
- **Troubleshooting**: Guia PATH_TROUBLESHOOTING.md atualizado com solução automática em destaque
- **CLI**: Adicionado comando `--setup-path` e `--help`

### Técnico
- Novas funções: `get_user_bin_path()`, `is_in_path()`, `get_shell_config_file()`
- Detecção automática de shell config (.bashrc, .zshrc, .bash_profile, config.fish)
- Script PowerShell para Windows (sem necessidade de admin)
- Validação automática de PATH após configuração

### Benefícios
- ✅ Zero configuração manual para usuários
- ✅ Funciona em todos os sistemas operacionais
- ✅ Sem necessidade de privilégios de administrador
- ✅ Fallback automático para alternativas (pipx)

## [1.3.1] - 2025-10-08

### Adicionado
- Menu interativo de opções quando o diretório não está vazio
- Opção de criar em ./agents-upstream (recomendado)
- Opção de criar em diretório com nome customizado
- Opção de continuar na pasta atual com warning
- Opção de cancelar instalação

### Melhorado
- Experiência do usuário Python agora idêntica ao pacote npx
- Mensagens coloridas e formatação melhorada
- Melhor feedback visual durante a instalação
- Validação de nomes de pastas

## [1.3.0] - 2025-10-08

### Adicionado
- Sistema completo de 9 agentes especializados
- 17+ templates profissionais para análise estratégica
- Sistema de telemetria anônima e opcional
- Documentação completa em português
- Comandos de gerenciamento de telemetria

### Funcionalidades
- Workflow automatizado de análise de problema (Agentes 0-5)
- Workflow de desenvolvimento de solução (Agentes 6-8)
- CLI interativo com menu de opções
- Integração com Cursor AI
- Estrutura de projeto completa

## Como usar este changelog

### Tipos de mudanças

- **Adicionado** - para novas funcionalidades
- **Modificado** - para mudanças em funcionalidades existentes
- **Obsoleto** - para funcionalidades que serão removidas em breve
- **Removido** - para funcionalidades removidas
- **Corrigido** - para correções de bugs
- **Mudanças de Segurança** - em caso de vulnerabilidades

### Versionamento

- **MAJOR** (X.0.0) - Mudanças incompatíveis com versões anteriores
- **MINOR** (1.X.0) - Novas funcionalidades compatíveis com versões anteriores
- **PATCH** (1.0.X) - Correções de bugs compatíveis com versões anteriores

[Unreleased]: https://github.com/seu-usuario/agents-upstream/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/seu-usuario/agents-upstream/releases/tag/v1.3.0

