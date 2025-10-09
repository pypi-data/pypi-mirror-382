import asyncio
import logging
from selenium.common.exceptions import WebDriverException
from .browserhandler import BrowserHandler
from .webpagehandler import WebPageHandler
import uuid
from uuid import uuid4
import time      
import random

# A configuração de logging global foi removida para evitar duplicação.
# A classe agora gerencia seu próprio logger.

class BrowserSessionManager:
    def __init__(self, max_instances=10):
        self.max_instances = max_instances
        self.active_sessions = []
        self.failed_attempts = 0
        self.queue = asyncio.Queue()

        # Cria e configura o logger
        #self.logger = logging.getLogger('').addHandler(console_handler)
        # Cria e configura o logger
        self.logger = logging.getLogger('BrowserSessionManager')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(filename='BrowserSessionManager.log', mode='w')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    async def initialize_session(self, site, profile, proxy, profile_folder, stealth_mode=False):
        if len(self.active_sessions) >= self.max_instances:
            self.logger.error("Maximum number of browser instances reached.")
            return None
        
        session_id = uuid4()
        try:
            browser_handler = BrowserHandler(site=site, profile=profile, proxy=proxy, profile_folder=profile_folder, stealth_mode=stealth_mode)
            web_handler = WebPageHandler(browser_handler.execute())
            session_info = {'id': session_id, 'handler': web_handler, 'params': {'site': site, 'profile': profile, 'proxy': proxy, 'profile_folder': profile_folder, 'stealth_mode': stealth_mode}}
            self.active_sessions.append(session_info)
            self.logger.info(f"Session {session_id} initialized successfully.")
            return session_info
        except Exception as e:
            self.logger.error(f"Error initiating browser session {session_id}: {e}")
            await self.handle_failure()
            return None

    async def handle_failure(self):
        self.failed_attempts += 1
        if self.failed_attempts < 3:
            self.logger.warning("Attempting to restart browser session...")
            await asyncio.sleep(1)  # Add a short delay before retry
        else:
            self.logger.error("Consecutive failures in starting browser session. Check connection or configurations.")

    async def close_session(self, session_info):
        if not session_info or 'handler' not in session_info:
            self.logger.error("Invalid session_info provided for closing.")
            return

        try:
            session_info['handler'].close()
            # Corrigido: Remover o dicionário da sessão, não apenas o ID.
            if session_info in self.active_sessions:
                self.active_sessions.remove(session_info)
                self.logger.info(f"Browser session {session_info.get('id')} closed and removed.")
            else:
                self.logger.warning(f"Attempted to close a session not found in active list: {session_info.get('id')}")
        except Exception as e:
            self.logger.error(f"Error closing browser session {session_info.get('id')}: {e}")

    async def restart_session(self, session_info):
        """ Restarts a specific session using its original parameters. """
        if not session_info or 'params' not in session_info:
            self.logger.error("Invalid session_info provided for restart.")
            return None
            
        session_id_to_restart = session_info.get('id')
        self.logger.info(f"Attempting to restart session {session_id_to_restart}...")
        
        # Fecha a sessão antiga antes de reiniciar
        await self.close_session(session_info)
        
        # Reinitialize session with the same parameters
        self.logger.info(f"Re-initializing session with params: {session_info['params']}")
        return await self.initialize_session(**session_info['params'])

    async def add_urls_to_queue(self, urls):
        for url in urls:
            await self.queue.put(url)

    async def process_url(self, url, scraper_function, site, profile, profile_folder, proxy=None, stealth_mode=False):
        session_id = str(uuid4())
        start_time = time.perf_counter()
        self.logger.info(f"[{session_id}] Starting URL processing: {url}")
        
        # Generalizado: Usa parâmetros em vez de valores fixos
        session_info = await self.initialize_session(site=site, profile=profile, proxy=proxy, profile_folder=profile_folder, stealth_mode=stealth_mode)
        
        if session_info is None:
            self.logger.error(f"[{session_id}] Failed to initialize session for URL: {url}. Skipping.")
            return

        web_handler = session_info['handler']
        try:
            await scraper_function(web_handler, url)
            end_time = time.perf_counter()
            duration = end_time - start_time
            self.logger.info(f"[{session_id}] Finished processing URL: {url} in {duration:.2f} seconds")
        except Exception as e:
            self.logger.error(f"[{session_id}] Error processing URL {url}: {e}")
        finally:
            await self.close_session(session_info)

    async def run_scraping_tasks(self, urls, scraper_function, site, profile, profile_folder, proxy=None, stealth_mode=False):
        await self.add_urls_to_queue(urls)
    
        async def process_queue():
            while not self.queue.empty():
                url = await self.queue.get()
                self.logger.info(f"Queue size before processing: {self.queue.qsize()}")

                start_time = time.time()
                task_id = hash(url) % 10000
                self.logger.info(f"[Task {task_id}] Starting URL processing: {url}")
                
                # Passa os parâmetros para process_url
                await self.process_url(url, scraper_function, site, profile, profile_folder, proxy, stealth_mode)

                await asyncio.sleep(random.randint(1, 5)) 
                self.logger.info(f"Queue size after processing: {self.queue.qsize()}")
                self.queue.task_done()
                end_time = time.time()
                self.logger.info(f"[Task {task_id}] Finished URL processing: {url} in {end_time - start_time:.2f} seconds")
        
        tasks = [asyncio.create_task(process_queue()) for _ in range(min(self.max_instances, len(urls)))]
        await asyncio.gather(*tasks)


'''if __name__ == "__main__":
    urls = ['https://www.google.com', 'https://www.wikipedia.org', 'https://www.python.org', 'https://www.github.com', 'https://www.stackoverflow.com']
    manager = BrowserSessionManager(max_instances=3)
    asyncio.run(manager.run_scraping_tasks(urls, lambda x, y: print(x, y)))
    print("All tasks completed.")
    logging.info("All tasks completed.")'''