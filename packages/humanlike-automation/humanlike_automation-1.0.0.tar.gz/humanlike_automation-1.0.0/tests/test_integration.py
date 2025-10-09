
import sys
import os
import pytest

# Adicionar o diretório pai ao path para importar a biblioteca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from humanlike_automation import BrowserHandler, WebPageHandler

# --- Testes de Integração para o Modo Normal ---

def test_normal_mode_initialization_and_navigation():
    """
    Testa se o BrowserHandler consegue iniciar em modo normal,
    navegar para uma URL e obter o título da página.
    """
    browser = None
    try:
        # 1. Configuração
        browser = BrowserHandler(
            site="https://www.google.com",
            profile="test_normal",
            profile_folder="profilestest/",
            use_stealth=False,
            headless=True  # Usar modo headless para testes
        )

        # 2. Execução
        driver = browser.execute()
        web_handler = WebPageHandler(driver)
        web_handler.open_link("https://www.google.com")

        # 3. Verificação (Assert)
        assert "Google" in driver.title

    finally:
        # 4. Limpeza
        if browser:
            browser.close()

def test_normal_mode_element_finding():
    """
    Testa a capacidade de encontrar um elemento na página em modo normal.
    """
    browser = None
    try:
        # 1. Configuração
        browser = BrowserHandler(
            site="https://www.google.com",
            profile="test_normal_elements",
            profile_folder="profilestest/",
            use_stealth=False,
            headless=True
        )
        driver = browser.execute()
        web_handler = WebPageHandler(driver)
        web_handler.open_link("https://www.google.com")

        # 2. Execução
        # Encontra a barra de pesquisa pelo seu nome
        search_bar = web_handler.get_element_by_xpath("//textarea[@name='q']")

        # 3. Verificação
        assert search_bar is not None
        assert search_bar.is_displayed()

    finally:
        # 4. Limpeza
        if browser:
            browser.close()

# --- Testes de Integração para o Modo Stealth ---

@pytest.mark.skip(reason="O modo Stealth pode exigir configurações específicas e download de drivers, pular por enquanto.")
def test_stealth_mode_initialization():
    """
    Testa se o BrowserHandler consegue iniciar em modo stealth.
    Este é um teste mais complexo e pode falhar se o navegador portátil
    não estiver configurado corretamente.
    """
    browser = None
    try:
        # 1. Configuração
        browser = BrowserHandler.create_stealth_browser(
            site="https://www.google.com",
            profile="test_stealth",
            headless=True
        )
        
        # 2. Execução
        status = browser.get_portable_browser_status()
        assert status.get('chrome_available', False) is True

        driver = browser.execute()
        web_handler = WebPageHandler(driver)
        web_handler.open_link("https://www.google.com")

        # 3. Verificação
        assert "Google" in driver.title

    finally:
        # 4. Limpeza
        if browser:
            browser.close()

