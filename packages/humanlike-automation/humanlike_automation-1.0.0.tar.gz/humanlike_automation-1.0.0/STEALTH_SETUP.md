# 🔒 Guia de Configuração do Modo Stealth

Este guia explica como configurar o modo stealth para máxima capacidade anti-detecção.

## 📋 Pré-requisitos

1. **Python 3.7+** instalado
2. **Dependências** instaladas: `pip install -r requirements.txt`

## 🚀 Configuração Rápida (Automática)

O modo stealth funciona automaticamente com o Chrome do sistema. Para usar:

```python
from humanlike_automation import BrowserHandler

# Criar browser em modo stealth
browser = BrowserHandler.create_stealth_browser(
    site="https://example.com",
    profile="meu_perfil",
    headless=False  # ou True para modo invisível
)

# Usar normalmente
driver = browser.execute()
```

## 🔧 Configuração Avançada (Chrome Portable)

Para máxima eficácia anti-detecção, use Chrome Portable:

### 1. Download do Chrome Portable

**Opção A: Download Manual (Recomendado)**
1. Acesse: https://portableapps.com/apps/internet/google_chrome_portable
2. Baixe e extraia para: `portable_browser/chrome/`
3. Estrutura esperada:
   ```
   portable_browser/
   ├── chrome/
   │   ├── GoogleChromePortable.exe  # ou chrome.exe
   │   └── ...
   ├── profiles/
   └── drivers/
   ```

**Opção B: Download Automático**
```python
from humanlike_automation import PortableBrowserManager

manager = PortableBrowserManager()
manager.download_chrome_portable()  # Orientações de download
manager.download_chromedriver()     # Download automático do driver
```

### 2. Verificar Status

```python
browser = BrowserHandler.create_stealth_browser("https://example.com")
status = browser.get_portable_browser_status()
print(status)
```

### 3. Configurar Automaticamente

```python
browser = BrowserHandler.create_stealth_browser("https://example.com")
browser.setup_portable_browser()  # Configura componentes necessários
```

## 🎯 Exemplos de Uso

### Exemplo Básico
```python
from humanlike_automation import BrowserHandler

# Modo stealth simples
browser = BrowserHandler.create_stealth_browser("https://example.com")
driver = browser.execute()

# Usar normalmente
driver.get("https://httpbin.org/headers")
print(driver.title)

browser.close()
```

### Exemplo com Configurações Personalizadas
```python
# Modo stealth com configurações avançadas
browser = BrowserHandler(
    site="https://example.com",
    profile="perfil_custom",
    use_stealth=True,
    headless=True,  # Modo invisível
    portable_browser_dir="./meu_chrome_portable"
)

driver = browser.execute()
# ... usar driver ...
browser.close()
```

### Teste de Anti-Detecção
```python
# Execute o exemplo de demonstração
# python examples/stealth_mode_demo.py

# Ou teste sites específicos
browser = BrowserHandler.create_stealth_browser("https://bot.sannysoft.com")
driver = browser.execute()
driver.get("https://bot.sannysoft.com")
# Verificar se passou no teste anti-bot
```

## 🛡️ Recursos Anti-Detecção

O modo stealth inclui:

- ✅ **undetected-chromedriver** - Driver Chrome especializado
- ✅ **User-Agent realista** - Simula navegador real
- ✅ **Perfis isolados** - Cookies e dados separados
- ✅ **JavaScript anti-detecção** - Remove assinaturas de bot
- ✅ **Configurações stealth** - Desabilita automação detectável
- ✅ **Comportamento humanizado** - Timing e movimentos naturais

## 📊 Sites de Teste

Teste a eficácia anti-detecção em:

1. **https://bot.sannysoft.com/** - Teste geral de bot
2. **https://httpbin.org/headers** - Verificar headers
3. **https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html** - Teste headless
4. **https://deviceandbrowserinfo.com/info_device** - Info do dispositivo

## 🔍 Troubleshooting

### Chrome não encontrado
```python
# Verificar status
browser = BrowserHandler.create_stealth_browser("https://example.com")
status = browser.get_portable_browser_status()
print("Chrome disponível:", status['chrome_available'])
print("Caminho:", status['chrome_path'])
```

### Driver não funciona
```python
# Reconfigurar driver
manager = PortableBrowserManager()
manager.download_chromedriver(force_download=True)
```

### Detecção ainda ocorre
1. Use Chrome Portable em vez do sistema
2. Evite padrões robóticos (delays fixos, cliques precisos)
3. Configure proxy se necessário
4. Use perfis diferentes para sites diferentes

## 📁 Estrutura de Arquivos

```
seu_projeto/
├── portable_browser/          # (criado automaticamente)
│   ├── chrome/               # Chrome Portable aqui
│   ├── profiles/             # Perfis de navegador
│   └── drivers/              # ChromeDriver
├── examples/
│   ├── stealth_mode_demo.py  # Demo completa stealth
│   └── demo_simple.py        # Demo com opção --stealth
└── seu_script.py
```

## ⚡ Exemplos Prontos

Execute os exemplos incluídos:

```bash
# Demo básica com stealth
python examples/demo_simple.py --stealth

# Demo completa anti-detecção
python examples/stealth_mode_demo.py

# YouTube com comportamento humano
python examples/youtube_human_behavior.py
```

## 🚨 Considerações Importantes

1. **Legalidade**: Use apenas em sites que você possui ou tem permissão
2. **Rate Limiting**: Respeite limites de requisições dos sites
3. **Termos de Uso**: Verifique ToS dos sites antes de automatizar
4. **Detectores Avançados**: Alguns sites têm detecção muito sofisticada

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs: `logging.basicConfig(level=logging.DEBUG)`
2. Teste com sites simples primeiro (httpbin.org)
3. Verifique configuração: `browser.get_portable_browser_status()`
4. Execute exemplos de teste para validar setup
