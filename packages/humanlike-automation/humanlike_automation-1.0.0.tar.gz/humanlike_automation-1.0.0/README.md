# 🤖 Humanlike-Automation Library

Uma biblioteca Python avançada para automação web com comportamento humano e capacidades anti-detecção.

## ✨ Principais Recursos

- 🔒 **Modo Stealth** - Anti-detecção avançada com undetected-chromedriver
- 🎭 **Comportamento Humano** - Simulação realista de ações de usuário
- 🌐 **Chrome Portable** - Suporte a instalações portáteis e isoladas
- ⚙️ **Configuração Flexível** - Gerenciamento centralizado de configs
- 📊 **Múltiplos Perfis** - Perfis isolados para diferentes sites
- 🔧 **Fácil de Usar** - API simples e intuitiva

## 🚀 Instalação Rápida

```bash
# Clonar repositório
git clone <seu-repo>
cd bot_infrastructure

# Instalar dependências
pip install -r humanlike_automation/requirements.txt

# Testar instalação
python examples/demo_simple.py
```

## 🎯 Uso Básico

### Modo Simples
```python
from humanlike_automation import BrowserHandler

# Criar browser handler
browser = BrowserHandler(
    site="https://example.com",
    profile="meu_perfil"
)

# Executar e usar
driver = browser.execute()
driver.get("https://example.com")
```

### Modo Stealth (Anti-Detecção)
```python
from humanlike_automation import BrowserHandler

# Criar browser em modo stealth
browser = BrowserHandler.create_stealth_browser(
    site="https://example.com",
    profile="stealth_profile",
    headless=False
)

# Usar normalmente - anti-detecção automática
driver = browser.execute()
```

## 📚 Exemplos Incluídos

```bash
# Demo básica
python examples/demo_simple.py

# Demo com modo stealth
python examples/demo_simple.py --stealth

# Teste completo anti-detecção
python examples/stealth_mode_demo.py

# YouTube com comportamento humano
python examples/youtube_human_behavior.py
```

## 🔒 Configuração do Modo Stealth

Para máxima eficácia anti-detecção, veja o [Guia de Configuração Stealth](STEALTH_SETUP.md).

### Configuração Rápida:
1. Execute: `python examples/stealth_mode_demo.py`
2. Se Chrome Portable não for encontrado, baixe de: https://portableapps.com/apps/internet/google_chrome_portable
3. Extraia para: `portable_browser/chrome/`

## 📁 Estrutura do Projeto

```
humanlike_automation/
├── browserhandler.py       # Gerenciamento principal do navegador
├── portable_browser.py     # Modo stealth e Chrome portable
├── config_manager.py       # Gerenciamento de configurações
├── webpagehandler.py       # Manipulação de páginas web
├── webpageanalyzer.py      # Análise de conteúdo
└── requirements.txt        # Dependências

examples/
├── demo_simple.py          # Demo básica
├── stealth_mode_demo.py    # Demo anti-detecção
├── youtube_human_behavior.py
└── README.md

config/
├── .env.example           # Configurações de ambiente
└── xpaths_config.json     # Configurações de XPaths
```

## ⚡ Funcionalidades Principais

### 🔒 Anti-Detecção
- undetected-chromedriver integrado
- Perfis stealth automatizados
- JavaScript anti-detecção
- User-agents realistas
- Configurações avançadas de Chrome

### 🎭 Comportamento Humano
- Delays naturais e variáveis
- Movimentos de mouse humanizados
- Scrolling orgânico
- Timing realista entre ações

### ⚙️ Configuração
- Variáveis de ambiente (.env)
- Configurações JSON centralizadas
- Múltiplos perfis de navegador
- XPaths configuráveis

## 🛠️ API Principal

### BrowserHandler
```python
# Modo tradicional
browser = BrowserHandler(
    site="https://example.com",
    profile="default",
    use_stealth=False
)

# Modo stealth
browser = BrowserHandler.create_stealth_browser(
    site="https://example.com",
    profile="stealth_profile"
)

# Verificar status
status = browser.get_portable_browser_status()
```

### PortableBrowserManager
```python
from humanlike_automation import PortableBrowserManager

manager = PortableBrowserManager()
driver = manager.create_stealth_driver(
    profile_name="meu_perfil",
    headless=True
)
```

## 🧪 Testes Anti-Detecção

Sites para testar eficácia:
- https://bot.sannysoft.com/
- https://httpbin.org/headers
- https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html

## 📋 Dependências

- selenium >= 4.13.0
- undetected-chromedriver >= 3.5.0
- webdriver-manager >= 4.0.0
- fake-useragent >= 2.0.0
- python-dotenv >= 1.0.0
- requests >= 2.28.0

## 🚨 Considerações Legais

⚠️ **IMPORTANTE**: Esta biblioteca deve ser usada apenas em:
- Sites que você possui
- Sites que autorizam automação
- Projetos de pesquisa/educação autorizados
- Conformidade com termos de uso

**Não use para**:
- Violar termos de serviço
- Scraping não autorizado
- Atividades maliciosas
- Contornar medidas de segurança legítimas

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit: `git commit -m 'Nova feature'`
4. Push: `git push origin minha-feature`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja `LICENSE` para detalhes.

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os exemplos em `examples/`
2. Consulte `STEALTH_SETUP.md` para configuração avançada
3. Execute testes: `python examples/stealth_mode_demo.py`