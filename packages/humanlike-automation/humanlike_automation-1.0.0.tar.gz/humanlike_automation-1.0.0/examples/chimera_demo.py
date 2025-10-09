import asyncio
import os
import sys
import time

# Adicionar o diretório pai ao path para importar a biblioteca
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from humanlike_automation.browsersessionmanager import BrowserSessionManager
from humanlike_automation.webpagehandler import WebPageHandler
from humanlike_automation.browserhandler import BrowserHandler
from chimera.core import ChimeraAgent

async def run_chimera_demo():
    print("Iniciando demonstração do Projeto Quimera...")

    # 1. Inicializar a infraestrutura base
    # Usamos use_stealth=False para simplificar e não depender do undetected_chromedriver para este teste.
    # Em um cenário real, use_stealth=True seria o padrão.
    browser_handler = None
    try:
        print("Inicializando BrowserHandler...")
        browser_handler = BrowserHandler(site="about:blank", use_stealth=False, headless=False)
        driver = browser_handler.execute()
        web_handler = WebPageHandler(driver)
        print("BrowserHandler inicializado.")

        # 2. Instanciar o agente Chimera
        print("Instanciando ChimeraAgent...")
        agent = ChimeraAgent(web_handler)
        print("ChimeraAgent instanciado.")

        # 3. Definir e executar um objetivo
        # Cenário do Gemini.md
        goal = "go to https://www.wikipedia.org and search for \"Artificial Intelligence\" and click on the search button"
        print(f"Executando objetivo: '{goal}'")
        agent.execute(goal)

        print("\nExemplo de execução do AgenticCore concluído.")
        input("Pressione Enter para fechar o navegador...")

    except Exception as e:
        print(f"Ocorreu um erro durante a execução do exemplo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if browser_handler and browser_handler.driver:
            print("Fechando o navegador...")
            browser_handler.close()
            print("Navegador fechado.")

if __name__ == "__main__":
    asyncio.run(run_chimera_demo())