# 📁 Exemplos de Uso - HumanLike Automation

Esta pasta contém exemplos práticos de como usar a biblioteca **humanlike-automation** para diferentes cenários de automação web.

## 🎯 **Exemplos Disponíveis:**

### 1. 🧪 **quick_test.py** - Teste Rápido
**O que faz:** Teste básico da biblioteca - acessa YouTube e reproduz o primeiro vídeo
**Ideal para:** Verificar se a biblioteca está funcionando

```bash
python quick_test.py
```

**Features demonstradas:**
- ✅ Inicialização básica do navegador
- ✅ Navegação para site
- ✅ Busca de elementos por XPath
- ✅ Clique em elementos
- ✅ Verificação de carregamento

---

### 2. 🎥 **youtube_random_player.py** - Player Aleatório
**O que faz:** Acessa YouTube, analisa vídeos da página inicial e reproduz um aleatório
**Ideal para:** Demonstrar automação básica com seleção inteligente

```bash
python youtube_random_player.py
```

**Features demonstradas:**
- ✅ Tratamento de popups (cookies, login)
- ✅ Busca múltipla de elementos
- ✅ Seleção aleatória
- ✅ Validação de elementos
- ✅ Scroll automático

---

### 3. 🧠 **youtube_human_behavior.py** - Comportamento Humano
**O que faz:** Simula navegação humana real com análise, delays e movimentos naturais
**Ideal para:** Demonstrar automação anti-detecção avançada

```bash
python youtube_human_behavior.py
```

**Features demonstradas:**
- ✅ Delays aleatórios humanizados
- ✅ Scroll natural e gradual
- ✅ Movimentos de mouse naturais
- ✅ Simulação de leitura/análise
- ✅ Processo de decisão humano
- ✅ Comportamentos durante reprodução

---

## 🛠️ **Como Executar:**

### **Pré-requisitos:**
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente (opcional)
cp .env.example .env
```

### **Executar exemplos:**
```bash
# Navegar para pasta de exemplos
cd examples

# Executar qualquer exemplo
python nome_do_exemplo.py
```

---

## 📊 **Comparação dos Exemplos:**

| Exemplo | Complexidade | Detecção | Tempo | Uso |
|---------|-------------|----------|-------|-----|
| `quick_test` | ⭐ Básico | ❌ Alto risco | ⚡ Rápido | 🧪 Teste |
| `youtube_random` | ⭐⭐ Médio | ⚠️ Médio risco | 🕐 Moderado | 🎯 Demo |
| `youtube_human` | ⭐⭐⭐ Avançado | ✅ Baixo risco | 🐌 Lento | 🥷 Produção |

---

## 🎓 **Conceitos Aprendidos:**

### **Exemplo 1 - Básico:**
- Inicialização de `BrowserHandler`
- Uso de `WebPageHandler`
- Busca por XPath simples
- Tratamento básico de erros

### **Exemplo 2 - Intermediário:**
- Múltiplas estratégias de busca
- Validação de elementos
- Seleção inteligente
- Tratamento de popups

### **Exemplo 3 - Avançado:**
- Comportamento humano simulado
- Anti-detecção avançada
- Delays e movimentos naturais
- Análise comportamental

---

## 🚀 **Criando Seus Próprios Exemplos:**

### **Template Básico:**
```python
from humanlike_automation import BrowserHandler, WebPageHandler

def meu_exemplo():
    # 1. Configurar navegador
    browser = BrowserHandler(
        site="https://exemplo.com",
        profile="meu_perfil",
        proxy=None,
        profile_folder="./profiles"
    )
    
    try:
        # 2. Iniciar e obter handlers
        driver = browser.execute()
        web_handler = WebPageHandler(driver)
        
        # 3. Sua automação aqui
        web_handler.open_link("https://exemplo.com")
        # ... sua lógica ...
        
    finally:
        # 4. Sempre fechar
        browser.close()

if __name__ == "__main__":
    meu_exemplo()
```

### **Dicas para Automação Eficaz:**

1. **🎭 Humanização:**
   - Use delays aleatórios
   - Varie padrões de movimento
   - Simule comportamento real

2. **🛡️ Anti-Detecção:**
   - Evite ações muito rápidas
   - Use perfis de navegador
   - Varie user agents

3. **📊 Robustez:**
   - Sempre trate exceções
   - Use múltiplas estratégias de busca
   - Valide elementos antes de usar

4. **🔧 Manutenibilidade:**
   - Use XPaths configuráveis
   - Modularize seu código
   - Documente bem

---

## 📞 **Precisa de Ajuda?**

- 📖 Veja o `README_PUBLIC.md` principal
- 🔧 Verifique o `.env.example` para configurações
- 🎯 Analise o `xpaths_config.json` para XPaths
- 💡 Consulte a documentação da biblioteca

---

**Divirta-se automatizando! 🤖✨**
