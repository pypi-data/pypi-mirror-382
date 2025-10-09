"""
Exemplo avançado: YouTube Human-like Browser
Demonstra comportamento humano mais realista:
1. Scroll natural pela página
2. Pausa para "ler" títulos
3. Movimento de mouse natural
4. Delays aleatórios
5. Simula interesse humano

Uso: python youtube_human_behavior.py
"""

import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from humanlike_automation import BrowserHandler, WebPageHandler, config_manager


class HumanYouTubeBrowser:
    def __init__(self):
        self.browser_handler = None
        self.web_handler = None
        self.driver = None
        
    def setup_browser(self):
        """Configura o navegador com comportamento humano"""
        print("🤖 Configurando navegador para comportamento humano...")
        
        self.browser_handler = BrowserHandler(
            site="https://www.youtube.com",
            profile="human_youtube",
            proxy=None,
            profile_folder="./profiles"
        )
        
        self.driver = self.browser_handler.execute()
        self.web_handler = WebPageHandler(self.driver)
        
        # Redimensionar janela para parecer mais humano
        self.driver.set_window_size(1366, 768)
        print("📏 Janela redimensionada para 1366x768")
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Delay aleatório para simular comportamento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"⏳ Pausando por {delay:.1f}s...")
        time.sleep(delay)
    
    def natural_scroll(self, direction="down", intensity=3):
        """Scroll natural e gradual"""
        print(f"📜 Fazendo scroll {direction} natural...")
        
        scroll_amount = random.randint(200, 400) * intensity
        if direction == "down":
            scroll_amount = abs(scroll_amount)
        else:
            scroll_amount = -abs(scroll_amount)
        
        # Scroll gradual para parecer humano
        steps = random.randint(3, 6)
        step_size = scroll_amount // steps
        
        for i in range(steps):
            self.driver.execute_script(f"window.scrollBy(0, {step_size});")
            time.sleep(random.uniform(0.1, 0.3))
    
    def move_mouse_naturally(self, element):
        """Move mouse de forma natural até um elemento"""
        try:
            actions = ActionChains(self.driver)
            
            # Movimento em curva natural
            actions.move_to_element(element)
            actions.perform()
            
            # Pausa como se estivesse lendo
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"⚠️ Erro no movimento do mouse: {e}")
    
    def simulate_reading_behavior(self):
        """Simula comportamento de leitura humana"""
        print("👀 Simulando leitura da página...")
        
        # Scroll inicial para ver o conteúdo
        self.natural_scroll("down", intensity=2)
        self.human_delay(2, 4)
        
        # Volta um pouco como se estivesse relendo
        self.natural_scroll("up", intensity=1)
        self.human_delay(1, 2)
        
        # Scroll final para decidir
        self.natural_scroll("down", intensity=1)
    
    def analyze_videos_like_human(self):
        """Analisa vídeos como um humano faria"""
        print("🔍 Analisando vídeos disponíveis...")
        
        # Buscar vídeos
        video_selectors = [
            "//a[@id='video-title']",
            "//a[contains(@class, 'ytd-video-renderer')]",
            "//ytd-rich-item-renderer//a[@id='video-title-link']"
        ]
        
        videos = []
        for selector in video_selectors:
            try:
                found_videos = self.web_handler.get_elements_by_xpath(selector)
                if found_videos:
                    videos.extend(found_videos[:15])  # Limitar a 15 vídeos
                    break
            except:
                continue
        
        if not videos:
            return None
        
        # Simular análise humana dos vídeos
        print("🧠 Simulando processo de decisão humana...")
        
        valid_videos = []
        for i, video in enumerate(videos):
            try:
                # Move mouse sobre o vídeo como se estivesse considerando
                self.move_mouse_naturally(video)
                
                href = video.get_attribute('href')
                title = video.get_attribute('title') or video.text
                
                if href and '/watch?v=' in href and title:
                    valid_videos.append({
                        'element': video,
                        'title': title.strip(),
                        'url': href,
                        'interest_score': random.randint(1, 10)  # Simula interesse
                    })
                    
                    print(f"📺 Analisando: {title[:50]}...")
                    
                # Pausa entre análises
                if i < len(videos) - 1:
                    self.human_delay(0.5, 1.5)
                    
            except Exception as e:
                print(f"⚠️ Erro analisando vídeo {i}: {e}")
                continue
        
        return valid_videos
    
    def choose_video_like_human(self, videos):
        """Escolhe vídeo baseado em 'interesse humano'"""
        if not videos:
            return None
        
        print("🎯 Aplicando critérios de seleção humanos...")
        
        # Simular preferências humanas
        # 70% chance de escolher por interesse, 30% aleatório
        if random.random() < 0.7:
            # Ordenar por interesse e escolher um dos top 3
            videos.sort(key=lambda x: x['interest_score'], reverse=True)
            top_videos = videos[:3]
            selected = random.choice(top_videos)
            print(f"🧠 Escolhido por interesse (score: {selected['interest_score']})")
        else:
            # Escolha completamente aleatória
            selected = random.choice(videos)
            print("🎲 Escolhido aleatoriamente")
        
        return selected
    
    def play_video_naturally(self, video):
        """Reproduz vídeo com comportamento natural"""
        print(f"🎬 Selecionado: {video['title']}")
        print(f"🔗 URL: {video['url']}")
        
        # Scroll até o vídeo
        self.driver.execute_script("arguments[0].scrollIntoView(true);", video['element'])
        self.human_delay(1, 2)
        
        # Move mouse e clica
        self.move_mouse_naturally(video['element'])
        print("🖱️ Clicando no vídeo...")
        video['element'].click()
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento do vídeo...")
        time.sleep(5)
        
        # Verificar se carregou
        try:
            video_player = self.web_handler.get_element_by_xpath("//video[@class='video-stream html5-main-video']")
            if video_player:
                print("✅ Vídeo carregado com sucesso!")
                
                # Simular assistir por um tempo
                watch_time = random.randint(15, 30)
                print(f"👁️ Assistindo por {watch_time} segundos...")
                
                # Durante a reprodução, simular comportamentos humanos
                for i in range(watch_time // 5):
                    time.sleep(5)
                    
                    # Ocasionalmente move o mouse
                    if random.random() < 0.3:
                        print("🖱️ Movimento natural do mouse...")
                        actions = ActionChains(self.driver)
                        actions.move_by_offset(random.randint(-50, 50), random.randint(-30, 30))
                        actions.perform()
                
                return True
            else:
                print("❌ Player não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro verificando player: {e}")
            return False
    
    def handle_popups(self):
        """Lida com popups de forma humana"""
        print("🍪 Verificando popups...")
        
        # Lista de possíveis popups para fechar
        popup_selectors = [
            "//button[contains(text(), 'Reject all')]",
            "//button[contains(text(), 'Rejeitar tudo')]",
            "//button[@aria-label='Dismiss']",
            "//button[@aria-label='Fechar']",
            "//button[contains(@class, 'dismiss')]"
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.web_handler.get_element_by_xpath(selector)
                if popup:
                    print(f"❌ Fechando popup: {selector}")
                    self.move_mouse_naturally(popup)
                    popup.click()
                    self.human_delay(1, 2)
            except:
                continue
    
    def run(self):
        """Executa o navegador humano do YouTube"""
        try:
            self.setup_browser()
            
            # Navegar para YouTube
            print("🌐 Navegando para YouTube...")
            self.web_handler.open_link("https://www.youtube.com")
            self.human_delay(3, 5)
            
            # Lidar com popups
            self.handle_popups()
            
            # Simular comportamento de leitura
            self.simulate_reading_behavior()
            
            # Analisar vídeos
            videos = self.analyze_videos_like_human()
            
            if not videos:
                print("❌ Nenhum vídeo encontrado")
                return False
            
            # Escolher vídeo
            selected_video = self.choose_video_like_human(videos)
            
            if not selected_video:
                print("❌ Não foi possível escolher um vídeo")
                return False
            
            # Reproduzir vídeo
            success = self.play_video_naturally(selected_video)
            
            return success
            
        except Exception as e:
            print(f"❌ Erro durante execução: {e}")
            return False
        
        finally:
            if self.browser_handler:
                print("🔚 Fechando navegador...")
                self.browser_handler.close()


def main():
    """Função principal"""
    print("=" * 60)
    print("🎥 YOUTUBE HUMAN-LIKE BROWSER")
    print("🤖 Simulando comportamento humano real")
    print("🧠 Com análise, delays e movimentos naturais")
    print("=" * 60)
    
    browser = HumanYouTubeBrowser()
    success = browser.run()
    
    if success:
        print("\n✅ Sessão humana concluída com sucesso!")
    else:
        print("\n❌ Falha na simulação humana")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
