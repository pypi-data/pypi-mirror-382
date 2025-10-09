"""
Script de teste rápido da biblioteca
Teste básico: acessa YouTube e clica no primeiro vídeo

Uso: python quick_test.py
"""

import time
from humanlike_automation import BrowserHandler, WebPageHandler


def quick_youtube_test():
    """Teste rápido: acessa YouTube e reproduz primeiro vídeo"""
    print("🚀 Teste rápido da biblioteca...")
    
    # Configurar navegador
    browser = BrowserHandler(
        site="https://www.youtube.com",
        profile="test",
        proxy=None,
        profile_folder="./profiles"
    )
    
    try:
        # Iniciar navegador
        print("📱 Iniciando navegador...")
        driver = browser.execute()
        web_handler = WebPageHandler(driver)
        
        # Ir para YouTube
        print("🌐 Acessando YouTube...")
        web_handler.open_link("https://www.youtube.com")
        time.sleep(5)
        
        # Fechar popup de cookies se existir
        try:
            web_handler.click_element("//button[contains(text(), 'Reject all')]")
            print("🍪 Popup de cookies fechado")
            time.sleep(2)
        except:
            print("ℹ️ Sem popup de cookies")
        
        # Buscar primeiro vídeo
        print("🔍 Buscando primeiro vídeo...")
        first_video = web_handler.get_element_by_xpath("//a[@id='video-title']")
        
        if first_video:
            title = first_video.get_attribute('title') or first_video.text
            print(f"🎬 Vídeo encontrado: {title[:50]}...")
            
            # Clicar no vídeo
            print("▶️ Clicando no vídeo...")
            first_video.click()
            time.sleep(5)
            
            # Verificar se carregou
            video_player = web_handler.get_element_by_xpath("//video")
            if video_player:
                print("✅ Vídeo carregado com sucesso!")
                print("🎵 Reproduzindo por 5 segundos...")
                time.sleep(5)
                return True
            else:
                print("❌ Player não encontrado")
                return False
        else:
            print("❌ Nenhum vídeo encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    finally:
        print("🔚 Fechando navegador...")
        browser.close()


if __name__ == "__main__":
    print("=" * 40)
    print("🧪 TESTE RÁPIDO DA BIBLIOTECA")
    print("=" * 40)
    
    success = quick_youtube_test()
    
    if success:
        print("\n✅ Teste passou!")
    else:
        print("\n❌ Teste falhou!")
    
    print("=" * 40)
