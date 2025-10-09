import random
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from .utility import *
from .browserhandler import *
from selenium.webdriver.support.ui import WebDriverWait


# Initialize logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class WebPageHandler:

    def __init__(self, driver):
        self.driver = driver
        self.utils = Utility()
        
    def printscreen(self):
        self.driver.save_screenshot('screenshot.png')
        
    def get_page_html(self):
        # Imprime o HTML da página para depuração
        page_html = self.driver.page_source

        return page_html

    def _wait_for_element(self, xpath, timeout=10, clickable=False):
        condition = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
        try:
            return WebDriverWait(self.driver, timeout).until(condition((By.XPATH, xpath)))
        except (TimeoutException, WebDriverException) as e:
            logger.warning(f"An error occurred while waiting for element: {e} xpath: {xpath}")
            return None
            #raise e  # Relançar a exceção para que o chamador saiba que algo falhou

    def find_elements_containing_text(self, text, timeout=10):
        xpath = f"//*[contains(text(), '{text}')]"
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            return self.driver.find_elements(By.XPATH, xpath)
        except (TimeoutException, WebDriverException):
            logger.error(f"Ocorreu um erro ao tentar encontrar elementos contendo o texto: {text}")
            return []

    def element_exists1(self, xpath, timeout=10):
        """
        Checks if an element exists on the page within a given timeout.
        """
        condition = EC.presence_of_element_located
        try:
            WebDriverWait(self.driver, timeout).until(condition((By.XPATH, xpath)))
            return True
        except (TimeoutException, WebDriverException):
            logger.error(f"An error occurred while trying to element exists : {xpath}")
            return False
        
    def element_exists(self, xpath, timeout=10):
        """
        Checks if an element exists on the page within a given timeout.
        """
        try:
            element = self._wait_for_element(xpath, timeout=timeout)
            return element is not None
        except (TimeoutException, WebDriverException):
            logger.error(f"An error occurred while checking for element: {xpath}")
            return False

    def click_element(self, xpath):
        """
        Clicks an element if it exists; logs an error otherwise.
        """
        try:
            if self.element_exists(xpath):
                #self.go_to_element(xpath)
                element = self._wait_for_element(xpath, clickable=True)
                if element:
                    element.click()
                    self._random_sleep()
                    return True
                else:    
                    logger.warning(f"Element not found: {xpath}")
                    return False
            else:
                logger.warning(f"Element not found: {xpath}")
                return False
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to element exists : {e}{xpath}")

    def click_element_on_element_xpath(self, elem, xpath):
        try:
            element_item =  elem.find_element(By.XPATH, xpath)
            if element_item:
                element_item.click()
                self._random_sleep()
                return True
            else:
                logger.warning(f"Element not found: {xpath}")
                return False
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to element exists : {e}{xpath}")
            return None            

    def get_element_on_element_xpath(self, elem, xpath):
        try:
            element_item =  elem.find_element(By.XPATH, xpath)
            if element_item:
                return element_item
            else:
                logger.warning(f"Element not found: {xpath}")
                return False
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to element exists : {e}{xpath}")
            return None          

    def _random_sleep(self, min_seconds=2, max_seconds=5):
        sleep_duration = random.uniform(min_seconds, max_seconds)
        logger.info(f"Sleeping for {sleep_duration:.2f} seconds.")
        time.sleep(sleep_duration)

    def go_to_element(self, xpath):
        element = self._wait_for_element(xpath, clickable=True)
        if element:
            ActionChains(self.driver).move_to_element(element).click().perform()
            self._random_sleep()

    def send_text(self, xpath, text):
        element = self._wait_for_element(xpath, clickable=True)
        if element:
            element.clear()
            self._random_sleep()
            element.send_keys(text)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self._random_sleep()

    def get_text_by_xpath(self, xpath, timeout=10):
        try:
            #if self.element_exists(xpath, timeout= 2):,
            element = self._wait_for_element(xpath, timeout=10, clickable=True)
            if element:
                return element.text
            else:
                logger.error(f"Element not found: {xpath}")
                return None
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to element exists : {e}{xpath}")
            return None
        
    def get_text_on_element(self, elem, xpath):
        try:
            element_item =  elem.find_element(By.XPATH, xpath)
            if element_item:
                return element_item.text
            else:
                logger.error(f"Element not found: {xpath}")
                return False
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to element exists : {e}{xpath}")
            return None    

    def get_link_by_xpath(self, xpath):
        try:
            link = self._wait_for_element(xpath, clickable=True)
            link.click()
            self._random_sleep()
            link = self.utils.paste_from_clipboard()
            if link:
                logger.info(f"Link found: {link}")
                return link
            else:
                logger.warning("Link element found, but it's empty.")
                return None
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to find the link: {e}")
            return None

    def get_elements_by_xpath(self, xpath):
        try:
            elements = self.driver.find_elements(By.XPATH, xpath)
            return elements
        except WebDriverException as e:
            logger.error(f"An error occurred while trying to find the elements: {e}")
            return None

    def get_element_by_xpath(self, xpath):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element
        except WebDriverException as e:
            logger.error(f"An error occurred while trying to find the element: {e}")
            return None

    def open_link(self, link):
        try:
            self.driver.get(link)
            element_present = EC.presence_of_element_located((By.TAG_NAME, 'body'))
            WebDriverWait(self.driver, 10).until(element_present)
            return True
        except WebDriverException as e:
            logging.error(f"An error occurred while trying to open the link: {e}")
            #self.handle_driver_failure()
            return False
        
    def handle_driver_failure(self):
        """Lida com falhas do driver reinicializando-o."""
        logging.error("Reinicializando o driver do navegador...")
        #self.driver.quit()  # Fecha o navegador atual
        #browser_handler = BrowserHandler(site=self.site, profile=profile, proxy=None, profile_folder=profile_folder)
        #self.driver = self.browser_handler.initialize_driver()  # Inicializa um novo navegador
        
    def get_xpath(self, element):
        """
        Generate unique XPath for a BeautifulSoup element.
        """
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            # Verifica se o elemento é o único do seu tipo entre os irmãos
            if len(siblings) == 1:
                components.append(child.name)
            else:
                # Conta a posição do elemento entre os irmãos do mesmo tipo
                count = 1
                for sibling in siblings:
                    if sibling == child:
                        break
                    if sibling.name == child.name:
                        count += 1
                components.append(f"{child.name}[{count}]")
            child = parent

        components.reverse()
        return '/'.join(components)
    
    def get_attribute_of_element(self, elem, xpath, attribute):
        try:
            element_item = elem.find_element(By.XPATH, xpath)
            if element_item:
                return element_item.get_attribute(attribute)
            else:
                logger.warning(f"Element not found for xpath: {xpath}")
                return None
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to get attribute '{attribute}': {e}{xpath}")
            return None

    def get_elements_by_tag(self, TAG):
        try:
            elements = self.driver.find_elements(By.TAG_NAME, TAG)
            return elements
        except WebDriverException as e:
            logger.error(f"An error occurred while trying to find the elements: {e}")
            return None
        
    def get_elements_by_tag_from_element(self, element, tag_name):
        """
        Returns a list of elements found within a specific element by tag name.

        :param element: The parent element to search within.
        :param tag_name: The tag name to search for.
        :return: A list of WebElement instances found; empty list if none are found.
        """
        try:
            return element.find_elements(By.TAG_NAME, tag_name)
        except WebDriverException as e:
            logger.error(f"Error finding elements by tag '{tag_name}': {e}")
            return []
        
    def close(self):
        self.driver.quit()
        logger.info("Browser session closed.")
        
    def get_element_by_css(self, css):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, css)
            return element
        except WebDriverException as e:
            logger.error(f"An error occurred while trying to find the element: {e}")
            return None


    def go_to_next_page(self, css):
        try:
            wait = WebDriverWait(self.driver, 10)
            while True:
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.artdeco-pagination__button--next")))
                    next_btn.location_once_scrolled_into_view 
                    time.sleep(0.2)
                    next_btn.click()
                    return True 
                except Exception as e:
                    self.driver.execute_script("window.scrollBy(0, 600);") 
                    time.sleep(1) 
        except Exception as e:
            self.logger.error(f"Failed to navigate to the next page: {e}")
            return False
        
    def get_attribute_by_xpath(self, xpath, attribute, timeout=10):
        """
        Retrieve the attribute value of an element found by XPath.
        
        :param xpath: The XPath used to locate the element.
        :param attribute: The attribute whose value needs to be retrieved.
        :param timeout: Time to wait for the element to be located.
        :return: The value of the specified attribute, or None if not found.
        """
        try:
            element = self._wait_for_element(xpath, timeout=timeout)
            if element:
                return element.get_attribute(attribute)
            else:
                logger.warning(f"Element not found for xpath: {xpath}")
                return None
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"An error occurred while trying to get attribute '{attribute}' for xpath '{xpath}': {e}")
            return None

    def upload_file(self, xpath, file_path):
        try:
            file_input = self.driver.find_element(By.XPATH, xpath)
            file_input.send_keys(file_path)
        except Exception as e:
            print(f"Failed to upload file: {e}")