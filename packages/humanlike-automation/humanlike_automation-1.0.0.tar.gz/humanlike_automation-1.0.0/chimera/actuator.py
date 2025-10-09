import logging
import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from humanlike_automation.webpagehandler import WebPageHandler

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def human_click(coords: tuple[int, int], web_handler: WebPageHandler):
    """
    Executa um clique de forma humana nas coordenadas fornecidas.

    Args:
        coords: Uma tupla com as coordenadas (x, y) do alvo.
        web_handler: A instância de WebPageHandler para interagir com o driver.
    """
    try:
        driver = web_handler.driver
        x, y = coords

        action = ActionChains(driver)
        
        # Move o mouse para o centro da tela primeiro para ter um ponto de partida consistente
        # ou para o elemento body para usar offsets relativos a ele.
        body = web_handler.get_body() # Assumindo que WebPageHandler tem um método get_body()
        if body:
            action.move_to_element(body).perform()
            # Move o mouse para as coordenadas alvo com um pequeno desvio aleatório
            action.move_by_offset(x - body.location['x'] + random.randint(-5, 5), y - body.location['y'] + random.randint(-5, 5)).perform()
        else:
            # Fallback se não conseguir encontrar o body, tenta mover para o canto superior esquerdo e então para o offset
            action.move_by_offset(x + random.randint(-5, 5), y + random.randint(-5, 5)).perform()

        # Pequena pausa antes do clique para simular hesitação
        time.sleep(random.uniform(0.1, 0.3))
        action.click().perform()

        # Pausa pós-clique
        time.sleep(random.uniform(0.2, 0.6))
        logger.info(f"[StealthActuator] Clique executado em ({x}, {y}).")

    except Exception as e:
        logger.error(f"[StealthActuator] Erro ao executar o clique humano: {e}", exc_info=True)

def human_type(text: str, web_handler: WebPageHandler):
    """
    Digita um texto de forma humana, caractere por caractere.

    Args:
        text: O texto a ser digitado.
        web_handler: A instância de WebPageHandler para interagir com o driver.
    """
    try:
        driver = web_handler.driver
        # Assume que o elemento correto já está focado pelo human_click
        # ou que o usuário irá focar o elemento antes de chamar human_type
        element = driver.switch_to.active_element
        
        logger.info(f"[StealthActuator] Digitando o texto: '{text}'")
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15)) # Pausa entre as teclas
        logger.info(f"[StealthActuator] Texto digitado com sucesso.")

    except Exception as e:
        logger.error(f"[StealthActuator] Erro ao executar a digitação humana: {e}", exc_info=True)

# Exemplo de uso (requer um driver de navegador ativo e uma página com elementos)
if __name__ == '__main__':
    from humanlike_automation.browserhandler import BrowserHandler
    import os

    # Caminho para a página de teste
    test_page_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_page.html'))
    test_page_url = f'file://{test_page_path}'

    try:
        # 1. Inicializar a infraestrutura base
        browser_handler = BrowserHandler(site=test_page_url, use_stealth=False, headless=False)
        driver = browser_handler.execute()
        web_handler = WebPageHandler(driver)
        web_handler.open_link(test_page_url)
        time.sleep(1) # Espera a página carregar

        # 2. Simular a localização de um elemento (coordenadas mockadas)
        # Estas coordenadas são aproximadas para os elementos na test_page.html
        input_coords = (130, 110) # Coordenadas do campo de input
        button_coords = (70, 150) # Coordenadas do botão

        # 3. Executar ações "humanas"
        print("--- Testando human_click e human_type ---")
        human_click(input_coords, web_handler)
        human_type("Texto digitado de forma humana!", web_handler)
        time.sleep(1)

        print("\n--- Testando human_click no botão ---")
        human_click(button_coords, web_handler)
        time.sleep(1)

        # Verificar o resultado na página
        message = web_handler.get_text_by_xpath("//p[@id='message']")
        print(f"\nMensagem na página: '{message}'")
        assert "Texto digitado de forma humana!" in message

        print("\nExemplo de execução do StealthActuator concluído com sucesso!")
        input("Pressione Enter para fechar o navegador...")

    except Exception as e:
        logger.error(f"Ocorreu um erro durante a execução do exemplo: {e}", exc_info=True)
    finally:
        if 'browser_handler' in locals() and browser_handler.driver:
            browser_handler.close()
