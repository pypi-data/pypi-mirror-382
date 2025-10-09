"""
Stealth Browser Example - demonstra o uso do modo stealth com Chrome portable
Este exemplo mostra como usar a biblioteca com máxima capacidade anti-detecção
"""

import os
import sys
import time
import logging

# Adicionar o diretório pai ao path para importar a biblioteca
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from humanlike_automation import BrowserHandler, PortableBrowserManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_stealth_mode():
    """Testa o modo stealth com detecção anti-bot."""
    
    print("=== Teste do Modo Stealth ===")
    
    # Criar browser handler em modo stealth
    browser = BrowserHandler.create_stealth_browser(
        site="https://httpbin.org/headers",
        profile="stealth_test",
        headless=False  # Definir como True para modo headless
    )
    
    try:
        # Verificar status do setup portable
        status = browser.get_portable_browser_status()
        print(f"Status do navegador portátil: {status}")
        
        # Tentar configurar navegador portátil se necessário
        if not status.get('chrome_available'):
            print("Chrome portátil não encontrado. Tentando configurar...")
            browser.setup_portable_browser()
        
        # Inicializar driver
        print("Inicializando driver em modo stealth...")
        driver = browser.execute()
        
        if driver:
            print("✓ Driver inicializado com sucesso!")
            
            # Testar navegação e detecção
            test_sites = [
                "https://httpbin.org/headers",
                "https://httpbin.org/user-agent", 
                "https://bot.sannysoft.com/",
                "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
            ]
            
            for site in test_sites:
                print(f"\n--- Testando: {site} ---")
                try:
                    driver.get(site)
                    time.sleep(3)
                    
                    # Capturar título da página
                    title = driver.title
                    print(f"Título da página: {title}")
                    
                    # Para sites de teste, capturar conteúdo relevante
                    if "httpbin.org" in site:
                        # Procurar por conteúdo JSON na página
                        page_source = driver.page_source
                        if "User-Agent" in page_source:
                            print("✓ User-Agent detectado na resposta")
                        if "webdriver" in page_source.lower():
                            print("⚠ Possível detecção de webdriver")
                        else:
                            print("✓ Nenhuma detecção de webdriver na resposta")
                    
                    elif "bot.sannysoft.com" in site:
                        # Verificar resultados do teste de bot
                        time.sleep(5)  # Aguardar carregamento completo
                        body_text = driver.find_element("tag name", "body").text
                        if "You are NOT a bot" in body_text:
                            print("✓ Passou no teste anti-bot")
                        elif "You are a bot" in body_text:
                            print("❌ Detectado como bot")
                        else:
                            print("? Status de bot indefinido")
                    
                    elif "intoli.com" in site:
                        # Verificar teste de headless
                        time.sleep(3)
                        page_text = driver.find_element("tag name", "body").text
                        if "Chrome headless detected" in page_text:
                            print("❌ Headless Chrome detectado")
                        else:
                            print("✓ Headless Chrome não detectado")
                    
                except Exception as e:
                    print(f"❌ Erro ao testar {site}: {e}")
                
                time.sleep(2)
        
        print("\n=== Teste de Comportamento Humano ===")
        
        # Simular comportamento humano
        driver.get("https://example.com")
        
        # Scroll suave
        for i in range(3):
            scroll_position = (i + 1) * 300
            driver.execute_script(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}});")
            time.sleep(1.5)
        
        # Mover mouse (simulado via JavaScript)
        driver.execute_script("""
            document.addEventListener('mousemove', function(e) {
                console.log('Mouse moved to:', e.clientX, e.clientY);
            });
            
            // Simular movimento de mouse
            var event = new MouseEvent('mousemove', {
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        """)
        
        print("✓ Comportamento humano simulado")
        
        # Aguardar um pouco antes de fechar
        print("\nAguardando 5 segundos antes de fechar...")
        time.sleep(5)
        
    except Exception as e:
        logger.error(f"Erro durante teste stealth: {e}")
        print(f"❌ Erro: {e}")
        
    finally:
        # Fechar navegador
        try:
            if browser.driver:
                browser.close()
                print("✓ Navegador fechado")
        except:
            pass


def test_portable_browser_manager():
    """Testa o PortableBrowserManager diretamente."""
    
    print("\n=== Teste do PortableBrowserManager ===")
    
    # Criar manager
    manager = PortableBrowserManager()
    
    # Verificar status
    status = manager.get_status()
    print(f"Status: {status}")
    
    # Tentar criar driver stealth diretamente
    try:
        driver = manager.create_stealth_driver(
            profile_name="test_direct",
            headless=False,
            use_undetected=True
        )
        
        print("✓ Driver stealth criado diretamente")
        
        # Teste rápido
        driver.get("https://httpbin.org/user-agent")
        time.sleep(3)
        
        print(f"Título: {driver.title}")
        
        driver.quit()
        print("✓ Driver fechado")
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")


def main():
    """Função principal."""
    print("🤖 Bot Infrastructure - Teste do Modo Stealth")
    print("=" * 50)
    
    try:
        # Testar modo stealth via BrowserHandler
        test_stealth_mode()
        
        # Testar PortableBrowserManager diretamente
        test_portable_browser_manager()
        
        print("\n" + "=" * 50)
        print("✅ Testes concluídos!")
        
    except KeyboardInterrupt:
        print("\n⏹ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        logger.exception("Erro durante execução dos testes")


if __name__ == "__main__":
    main()
