import time
from database_handler import Database_handler
from apscheduler.schedulers.background import BackgroundScheduler

db_handler = Database_handler()

class ServicesHandler:
    def __init__(self):
        self.db_handler = db_handler
        scheduler = BackgroundScheduler()    
        scheduler.add_job(db_handler.run_scheduled_scripts, 'interval', minutes=1)
        scheduler.start()

        # Mantém o script rodando para que o agendador possa executar trabalhos
        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()


    # Mantém o script rodando pa

    def execute_action(self, action, process_id):
        try:
            # Simular a execução de uma ação (pode ser substituído pela lógica real)
            print(f"Executando ação: {action.type_action} com xpath: {action.xpath}")

            # Registrar início da ação
            self.db_handler.log_action(process_id, action.id, "Iniciado", "Ação iniciada")
            
            # Aqui você colocaria a lógica real de execução da ação
            # ...

            # Registrar conclusão da ação
            self.db_handler.log_action(process_id, action.id, "Concluído", "Ação concluída com sucesso")
        except Exception as e:
            # Registrar falha da ação
            self.db_handler.log_action(process_id, action.id, "Erro", f"Erro na execução: {e}")
     
def main():
    db_handler = Database_handler()
    services_handler = ServicesHandler(db_handler)
    print("Tabelas criadas com sucesso.")

    while True:
        active_processes = db_handler.get_active_processes()
        for process in active_processes:
            pending_actions = db_handler.get_pending_actions()
            for action in pending_actions:
                services_handler.execute_action(action, process.id)
            
            # Atualizar o status do processo para 'Concluído'
            db_handler.update_process_status(process.id, "Concluído")

        time.sleep(60)  # Espera 60 segundos antes de verificar novamente

if __name__ == "__main__":
    main()
