# Guia de Publicação no PyPI

Este guia explica como publicar o pacote `agents-upstream` no PyPI.

## 📋 Pré-requisitos

1. **Instalar ferramentas de build/publicação:**
   ```bash
   pip install build twine
   ```
   > ⚠️ **IMPORTANTE:** Execute isso antes de qualquer comando de build ou publicação!

2. **Conta no PyPI:**
   - Crie uma conta em: https://pypi.org/account/register/
   - Verifique seu email

3. **Conta no TestPyPI (recomendado para testes):**
   - Crie uma conta em: https://test.pypi.org/account/register/

4. **Configurar API Token:**
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

## 🧪 Testar Localmente Primeiro

Antes de publicar, sempre teste localmente:

```bash
# Entre na pasta do pacote Python
cd python-package

# Instale em modo editável
pip install -e .

# Teste o comando
agents-upstream

# Se funcionar, desinstale
pip uninstall agents-upstream
```

## 🏗️ Build do Pacote

```bash
cd python-package

# Limpar builds anteriores
rm -rf dist/ build/ *.egg-info/

# Criar distribuição
python -m build
```

Isso criará dois arquivos em `dist/`:
- `agents-upstream-1.3.0.tar.gz` (código fonte)
- `agents_upstream-1.3.0-py3-none-any.whl` (wheel)

## 🧪 Testar no TestPyPI (Recomendado)

```bash
# Upload para TestPyPI
python -m twine upload --repository testpypi dist/*

# Instalar do TestPyPI para testar
pip install --index-url https://test.pypi.org/simple/ agents-upstream

# Testar
agents-upstream

# Desinstalar após teste
pip uninstall agents-upstream
```

## 🚀 Publicar no PyPI

**ATENÇÃO:** Esta é a publicação oficial. Certifique-se de que tudo está correto!

```bash
# Upload para PyPI oficial
python -m twine upload dist/*

# Será solicitado:
# Username: __token__
# Password: pypi-AgEIcHlwaS5vcmcC... (seu token API)
```

## 📦 Configurar ~/.pypirc (Opcional)

Para evitar digitar credenciais toda vez:

```bash
# Criar arquivo ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-SEU_TOKEN_AQUI

[testpypi]
username = __token__
password = pypi-SEU_TOKEN_TESTPYPI_AQUI
EOF

# Proteger o arquivo
chmod 600 ~/.pypirc
```

Então você pode publicar sem digitar credenciais:

```bash
# TestPyPI
python -m twine upload --repository testpypi dist/*

# PyPI
python -m twine upload dist/*
```

## 🔄 Atualizando uma Versão

1. **Atualizar versão:**
   ```bash
   # Editar versão em:
   # - python-package/pyproject.toml
   # - python-package/setup.py
   # - python-package/agents_upstream/__init__.py
   ```

2. **Atualizar CHANGELOG.md:**
   ```bash
   # Documentar mudanças
   ```

3. **Rebuild e republish:**
   ```bash
   rm -rf dist/ build/ *.egg-info/
   python -m build
   python -m twine upload dist/*
   ```

## ✅ Verificar Publicação

Após publicar, verifique:

1. **Página do PyPI:**
   - https://pypi.org/project/agents-upstream/

2. **Testar instalação:**
   ```bash
   # Criar ambiente limpo
   python -m venv test-env
   source test-env/bin/activate
   
   # Instalar do PyPI
   pip install agents-upstream
   
   # Testar
   agents-upstream
   
   # Limpar
   deactivate
   rm -rf test-env
   ```

3. **Testar instalação de usuário (sem privilégios admin):**
   ```bash
   # Testar instalação como usuário comum
   pip install --user agents-upstream
   
   # O pacote deve detectar e oferecer configurar PATH automaticamente
   agents-upstream
   
   # Testar configuração automática de PATH
   agents-upstream --setup-path
   
   # Verificar se comando está disponível
   which agents-upstream  # deve mostrar o caminho
   
   # Desinstalar após teste
   pip uninstall agents-upstream
   ```

4. **Testar com pipx:**
   ```bash
   pipx run agents-upstream
   ```

### 📌 Nota Importante sobre PATH do Usuário

Quando usuários instalam o pacote **sem privilégios de administrador** (usando `pip install --user`), o executável é instalado em:
- **Linux/Mac:** `~/.local/bin/`
- **Windows:** `%APPDATA%\Python\Python3X\Scripts\`

Esses diretórios precisam estar no PATH do usuário. A documentação do README.md já inclui instruções para configurar isso. Certifique-se de:

✅ **README.md contém instruções de PATH** (verificar seção "Via pip (instalação global)")  
✅ **Testar instalação com `pip install --user` antes de publicar**  
✅ **Recomendar pipx como alternativa** (gerencia PATH automaticamente)

## 🔒 Segurança

- ✅ **NUNCA** commite tokens API no Git
- ✅ Use API tokens, não senha
- ✅ Proteja `~/.pypirc` com `chmod 600`
- ✅ Revogue tokens antigos ao criar novos

## 🐛 Troubleshooting

### Erro: "File already exists"
```bash
# Não pode republicar mesma versão
# Solução: Incrementar versão no pyproject.toml
```

### Erro: "Invalid or non-existent authentication"
```bash
# Token incorreto ou expirado
# Solução: Gerar novo token no PyPI
```

### Pacote não aparece no PyPI
```bash
# Aguarde 1-2 minutos para indexação
# Verifique em: https://pypi.org/project/agents-upstream/
```

## 📚 Links Úteis

- **PyPI:** https://pypi.org/project/agents-upstream/
- **TestPyPI:** https://test.pypi.org/project/agents-upstream/
- **Twine Docs:** https://twine.readthedocs.io/
- **Packaging Python:** https://packaging.python.org/
- **PATH Troubleshooting:** [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md) - Guia para usuários com problemas de PATH

## 🎯 Checklist Antes de Publicar

- [ ] Versão atualizada em todos os arquivos
- [ ] CHANGELOG.md atualizado
- [ ] README.md revisado
- [ ] Testado localmente
- [ ] Build sem erros
- [ ] Testado no TestPyPI
- [ ] Pronto para publicação oficial!

