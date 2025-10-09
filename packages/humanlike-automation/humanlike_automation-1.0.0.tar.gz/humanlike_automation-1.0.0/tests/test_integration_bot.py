
import pytest
import asyncio
import os
from humanlike_automation.browsersessionmanager import BrowserSessionManager

@pytest.mark.asyncio
async def test_bot_integration():
    # O caminho para o arquivo de teste HTML
    # Usamos um caminho absoluto para garantir que o teste funcione de qualquer diretório
    test_page_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_page.html'))
    test_page_url = f'file://{test_page_path}'

    # 1. Inicializar o gerenciador de sessão
    manager = BrowserSessionManager(max_instances=1)

    # 2. Iniciar uma nova sessão
    # Para testes locais, não precisamos de proxy ou perfil complexo
    session_info = await manager.initialize_session(site=None, profile=None, proxy=None, profile_folder=None)
    assert session_info is not None, "Falha ao inicializar a sessão do navegador"

    web_handler = session_info['handler']

    try:
        # 3. Navegar para a página de teste local
        web_handler.open_link(test_page_url)

        # 4. Ações e Assertivas
        # Verificar o título da página
        expected_title = "Test Page"
        actual_title = web_handler.driver.title
        assert actual_title == expected_title, f"Título da página incorreto. Esperado: {expected_title}, Obtido: {actual_title}"

        # Encontrar o input, digitar texto e verificar
        input_xpath = "//input[@id='test_input']"
        test_text = "hello world"
        web_handler.send_text(input_xpath, test_text)
        
        # Para verificar o valor, usamos execute_script pois o valor de um input não é seu 'text'
        entered_text = web_handler.driver.execute_script(f"return document.getElementById('test_input').value")
        assert entered_text == test_text, f"Texto do input incorreto. Esperado: {test_text}, Obtido: {entered_text}"

        # Clicar no botão
        button_xpath = "//button[@id='test_button']"
        web_handler.click_element(button_xpath)

        # Verificar a mensagem que aparece após o clique
        message_xpath = "//p[@id='message']"
        # Damos um pequeno tempo para o JavaScript da página executar
        await asyncio.sleep(1)
        message_text = web_handler.get_text_by_xpath(message_xpath)
        expected_message = f"Button clicked! You entered: {test_text}"
        assert message_text == expected_message, f"Mensagem pós-clique incorreta. Esperado: '{expected_message}', Obtido: '{message_text}'"

    finally:
        # 5. Encerrar a sessão de forma limpa
        await manager.close_session(session_info)

