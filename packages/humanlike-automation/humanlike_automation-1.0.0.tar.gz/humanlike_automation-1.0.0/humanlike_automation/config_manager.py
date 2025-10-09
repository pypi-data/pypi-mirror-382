import os
import json
from dotenv import load_dotenv


class ConfigManager:
    """Gerenciador centralizado de configurações para a biblioteca."""
    
    def __init__(self, env_file='.env', xpaths_file='xpaths_config.json'):
        self.env_file = env_file
        self.xpaths_file = xpaths_file
        self._load_environment()
        self._load_xpaths()
    
    def _load_environment(self):
        """Carrega variáveis de ambiente do arquivo .env"""
        load_dotenv(self.env_file)
    
    def _load_xpaths(self):
        """Carrega configurações de XPaths do arquivo JSON"""
        try:
            with open(self.xpaths_file, 'r', encoding='utf-8') as f:
                self.xpaths = json.load(f)
        except FileNotFoundError:
            self.xpaths = {}
    
    def get_env(self, key, default=None):
        """Obtém variável de ambiente"""
        return os.getenv(key, default)
    
    def get_xpath(self, site, category, element):
        """Obtém XPath específico para um site/categoria/elemento"""
        try:
            return self.xpaths[site][category][element]
        except KeyError:
            raise ValueError(f"XPath não encontrado: {site}.{category}.{element}")
    
    def get_all_xpaths(self, site, category=None):
        """Obtém todos os XPaths de um site ou categoria"""
        try:
            if category:
                return self.xpaths[site][category]
            return self.xpaths[site]
        except KeyError:
            return {}
    
    def get_database_config(self):
        """Obtém configuração completa do banco de dados"""
        return {
            'host': self.get_env('DB_HOST', 'localhost'),
            'user': self.get_env('DB_USER', 'root'),
            'password': self.get_env('DB_PASSWORD', ''),
            'database': self.get_env('DB_NAME', 'default_db')
        }
    
    def get_database_uri(self):
        """Retorna URI de conexão do banco de dados"""
        config = self.get_database_config()
        return f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
    
    def get_telegram_config(self):
        """Obtém configuração do Telegram Bot"""
        return {
            'token': self.get_env('TELEGRAM_BOT_TOKEN'),
            'chat_id': self.get_env('TELEGRAM_CHAT_ID')
        }
    
    def get_openai_config(self):
        """Obtém configuração da OpenAI"""
        return {
            'api_key': self.get_env('OPENAI_API_KEY')
        }


# Instância global para uso fácil
config_manager = ConfigManager()
