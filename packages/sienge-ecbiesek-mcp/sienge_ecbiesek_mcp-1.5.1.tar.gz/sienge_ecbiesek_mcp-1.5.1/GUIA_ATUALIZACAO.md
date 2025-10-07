# 🔄 GUIA DE ATUALIZAÇÃO - SIENGE ECBIESEK MCP

## 📋 **PROCESSO COMPLETO DE ATUALIZAÇÃO**

### **1. 📝 FAZER MUDANÇAS NO CÓDIGO**
- Editar `src/sienge_mcp/server.py` ou outros arquivos
- Testar localmente primeiro

### **2. 🔢 ATUALIZAR VERSÃO**
Editar `pyproject.toml`:
```toml
[project]
version = "1.0.1"  # Incrementar versão
```

**Regras de Versionamento:**
- `1.0.1` - Correção de bugs (patch)
- `1.1.0` - Novas funcionalidades (minor)
- `2.0.0` - Mudanças que quebram compatibilidade (major)

### **3. 🏗️ REBUILD DO PACKAGE**
```bash
# Limpar build anterior
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue

# Build nova versão
.\.venv\Scripts\python.exe -m build
```

### **4. 🧪 TESTAR NOVA VERSÃO**
```bash
# Instalar nova versão localmente
.\.venv\Scripts\python.exe -m pip install ./dist/sienge_ecbiesek_mcp-1.0.1-py3-none-any.whl --force-reinstall

# Testar comando
.\.venv\Scripts\sienge-ecbiesek-mcp.exe
```

### **5. 📤 PUBLICAR ATUALIZAÇÃO**
```bash
# Upload nova versão para PyPI
.\.venv\Scripts\twine.exe upload dist/sienge_ecbiesek_mcp-1.0.1-py3-none-any.whl
```

### **6. ✅ VERIFICAR PUBLICAÇÃO**
- Acessar: https://pypi.org/project/sienge-ecbiesek-mcp/
- Confirmar nova versão disponível

---

## 🚀 **SCRIPT AUTOMATIZADO DE ATUALIZAÇÃO**

Crie um arquivo `atualizar.ps1`:

```powershell
# Atualizar versão (manual no pyproject.toml primeiro!)
Write-Host "=== LIMPANDO BUILD ANTERIOR ==="
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "=== BUILDANDO NOVA VERSÃO ==="
.\.venv\Scripts\python.exe -m build

Write-Host "=== TESTANDO LOCALMENTE ==="
$wheelFile = Get-ChildItem -Path "dist\*.whl" | Select-Object -First 1
.\.venv\Scripts\python.exe -m pip install $wheelFile.FullName --force-reinstall

Write-Host "=== PUBLICANDO NO PYPI ==="
.\.venv\Scripts\twine.exe upload $wheelFile.FullName

Write-Host "=== CONCLUÍDO! ==="
```

---

## 📋 **CHECKLIST DE ATUALIZAÇÃO**

- [ ] **Fazer mudanças** no código
- [ ] **Testar localmente** com credenciais reais
- [ ] **Atualizar versão** no `pyproject.toml`
- [ ] **Limpar build** anterior
- [ ] **Build nova versão**
- [ ] **Testar nova versão** localmente
- [ ] **Publicar no PyPI**
- [ ] **Verificar** no site do PyPI
- [ ] **Avisar equipe** sobre atualização

---

## 🔄 **ATUALIZAÇÕES AUTOMÁTICAS PARA USUÁRIOS**

Como você usa `@latest` na configuração:
```json
"sienge-ecbiesek-mcp@latest"
```

Os usuários **automaticamente** pegam a versão mais recente quando:
- Reiniciam o Claude Desktop
- O pipx atualiza o cache

---

## ⚡ **TIPOS DE ATUALIZAÇÕES COMUNS**

### **🐛 Correção de Bug**
```bash
# 1.0.0 → 1.0.1
# Exemplo: Corrigir erro de autenticação
```

### **✨ Nova Funcionalidade**
```bash
# 1.0.1 → 1.1.0
# Exemplo: Adicionar nova ferramenta do Sienge
```

### **💥 Mudança Maior**
```bash
# 1.1.0 → 2.0.0
# Exemplo: Mudar formato de configuração
```

---

## 🎯 **DICA PRO**

**Sempre teste localmente antes de publicar!** Use o arquivo wheel local para validar mudanças com suas credenciais reais do Sienge.

---

**Quer que eu crie o script automatizado de atualização para você?** 🤔
