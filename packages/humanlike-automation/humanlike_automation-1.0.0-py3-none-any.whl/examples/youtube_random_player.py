"""
Exemplo simples: YouTube Random Video Player
Demonstra o uso da biblioteca humanlike-automation para:
1. Acessar o YouTube
2. Selecionar um vídeo aleatório da página inicial
3. Reproduzir o vídeo

Uso: python youtube_random_player.py
"""

import random
import time
from humanlike_automation import BrowserHandler, WebPageHandler, config_manager


def play_random_youtube_video():
    """
    Acessa o YouTube e reproduz um vídeo aleatório da página inicial
    """
    print("🎥 Iniciando YouTube Random Video Player...")
    
    # Configurar o navegador
    browser_handler = BrowserHandler(
        site="https://www.youtube.com",
        profile="youtube_player",
        proxy=None,
        profile_folder="./profiles"
    )
    
    try:
        # Obter driver do navegador
        print("🚀 Iniciando navegador...")
        driver = browser_handler.execute()
        
        # Criar handler para interações
        web_handler = WebPageHandler(driver)
        
        # Navegar para YouTube
        print("📱 Acessando YouTube...")
        web_handler.open_link("https://www.youtube.com")
        
        # Aguardar carregamento da página
        print("⏳ Aguardando carregamento...")
        time.sleep(3)
        
        # Fechar possíveis popups de cookies/login
        try:
            # Tentar fechar popup de cookies
            reject_button = web_handler.get_element_by_xpath("//button[contains(text(), 'Reject all')]")
            if reject_button:
                print("🍪 Fechando popup de cookies...")
                web_handler.click_element("//button[contains(text(), 'Reject all')]")
                time.sleep(1)
        except:
            pass
        
        try:
            # Tentar fechar popup de login se aparecer
            dismiss_button = web_handler.get_element_by_xpath("//button[@aria-label='Dismiss']")
            if dismiss_button:
                print("❌ Fechando popup de login...")
                web_handler.click_element("//button[@aria-label='Dismiss']")
                time.sleep(1)
        except:
            pass
        
        # Buscar vídeos na página inicial
        print("🔍 Buscando vídeos na página inicial...")
        
        # XPath para vídeos da página inicial do YouTube
        video_selectors = [
            "//a[@id='video-title']",  # Títulos de vídeos
            "//a[contains(@class, 'ytd-video-renderer')]",  # Links de vídeos
            "//ytd-rich-item-renderer//a[@id='video-title-link']"  # Vídeos em rich format
        ]
        
        videos = []
        for selector in video_selectors:
            try:
                found_videos = web_handler.get_elements_by_xpath(selector)
                if found_videos:
                    videos.extend(found_videos)
                    break
            except:
                continue
        
        if not videos:
            print("❌ Nenhum vídeo encontrado na página inicial")
            return False
        
        # Filtrar vídeos válidos (que têm href)
        valid_videos = []
        for video in videos[:20]:  # Pegar apenas os primeiros 20 para não sobrecarregar
            try:
                href = video.get_attribute('href')
                title = video.get_attribute('title') or video.text
                if href and '/watch?v=' in href and title:
                    valid_videos.append({
                        'element': video,
                        'title': title.strip(),
                        'url': href
                    })
            except:
                continue
        
        if not valid_videos:
            print("❌ Nenhum vídeo válido encontrado")
            return False
        
        # Selecionar vídeo aleatório
        selected_video = random.choice(valid_videos)
        print(f"🎲 Vídeo selecionado: {selected_video['title']}")
        print(f"🔗 URL: {selected_video['url']}")
        
        # Scroll até o vídeo para garantir que esteja visível
        driver.execute_script("arguments[0].scrollIntoView(true);", selected_video['element'])
        time.sleep(1)
        
        # Clicar no vídeo selecionado
        print("▶️ Reproduzindo vídeo...")
        selected_video['element'].click()
        
        # Aguardar carregamento do vídeo
        print("⏳ Aguardando carregamento do vídeo...")
        time.sleep(5)
        
        # Verificar se o vídeo está carregando/reproduzindo
        try:
            video_player = web_handler.get_element_by_xpath("//video[@class='video-stream html5-main-video']")
            if video_player:
                print("✅ Vídeo carregado com sucesso!")
                print("🎵 Reproduzindo...")
                
                # Deixar reproduzir por 10 segundos como demonstração
                print("⏰ Reproduzindo por 10 segundos...")
                time.sleep(10)
                
                return True
            else:
                print("⚠️ Player de vídeo não encontrado")
                return False
                
        except Exception as e:
            print(f"⚠️ Erro ao verificar player: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False
    
    finally:
        # Fechar navegador
        print("🔚 Fechando navegador...")
        try:
            browser_handler.close()
        except:
            pass


def main():
    """Função principal"""
    print("=" * 50)
    print("🎥 YOUTUBE RANDOM VIDEO PLAYER")
    print("🤖 Usando humanlike-automation")
    print("=" * 50)
    
    success = play_random_youtube_video()
    
    if success:
        print("\n✅ Execução concluída com sucesso!")
    else:
        print("\n❌ Execução falhou")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
