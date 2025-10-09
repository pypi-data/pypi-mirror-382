import json
import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from apscheduler.schedulers.background import BackgroundScheduler
from .config_manager import config_manager


Base = declarative_base()

class HomeAction(Base):
    __tablename__ = 'home_action'
    id = Column(Integer, primary_key=True)
    type_action = Column(String(255))
    xpath = Column(String(255))
    value = Column(String(255))
    procedure_id = Column(Integer, ForeignKey('home_procedure.id'))

class ProcessTrigger(Base):
    __tablename__ = 'process_trigger'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('home_bot.id'))
    status = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProcessLog(Base):
    __tablename__ = 'process_log'
    id = Column(Integer, primary_key=True)
    trigger_id = Column(Integer, ForeignKey('process_trigger.id'))
    action_id = Column(Integer, ForeignKey('home_action.id'))
    status = Column(String(255))
    message = Column(String(255))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class HomeBot(Base):
    __tablename__ = 'home_bot'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
class ScriptSchedule(Base):
    __tablename__ = 'script_schedule'
    id = Column(Integer, primary_key=True)
    script_name = Column(String)
    script_path = Column(String)
    frequency = Column(Integer)  # Frequency in minutes
    next_run = Column(DateTime, default=datetime.datetime.utcnow)
    last_run = Column(DateTime)


class Database_handler:
    def __init__(self, config_path=None):
        # Configuração do banco de dados
        if config_path is None:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            config_path = os.path.join(dir_path, 'db_config.json')
        
        if not os.path.isfile(config_path):
            # Se não existe o arquivo local, usa o config_manager
            DATABASE_URI = config_manager.get_database_uri()
        else:
            # Mantém compatibilidade com arquivo de config existente
            with open(config_path, 'r') as f:
                config = json.load(f)
            DATABASE_URI = f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
        
        self.engine = create_engine(DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        # Criação das tabelas no banco de dados
        Base.metadata.create_all(self.engine)

    def get_pending_actions(self):
        session = self.Session()
        pending_actions = session.query(HomeAction).filter(HomeAction.status == 'Pending').all()
        session.close()
        return pending_actions

    def initialize_process(self, bot_id):
        session = self.Session()
        new_trigger = ProcessTrigger(bot_id=bot_id, status='Started')
        session.add(new_trigger)
        session.commit()
        trigger_id = new_trigger.id
        session.close()
        return trigger_id

    def log_action(self, trigger_id, action_id, status, message):
        session = self.Session()
        new_log = ProcessLog(trigger_id=trigger_id, action_id=action_id, status=status, message=message)
        session.add(new_log)
        session.commit()
        session.close()

    def complete_process(self, trigger_id):
        session = self.Session()
        trigger = session.query(ProcessTrigger).get(trigger_id)
        if trigger:
            trigger.status = 'Completed'
            trigger.updated_at = datetime.datetime.utcnow()
            session.commit()
        session.close()

    def schedule_script(self, script_name, script_path, frequency_minutes):
        session = self.Session()
        next_run_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=frequency_minutes)
        scheduled_script = ScriptSchedule(
            script_name=script_name,
            script_path=script_path,
            frequency=frequency_minutes,
            next_run=next_run_time
        )
        session.add(scheduled_script)
        session.commit()
        session.close()

    def get_due_scripts(self):
        session = self.Session()
        current_time = datetime.datetime.utcnow()
        due_scripts = session.query(ScriptSchedule).filter(ScriptSchedule.next_run <= current_time).all()
        session.close()
        return due_scripts

    def update_script_run_time(self, script_id):
        session = self.Session()
        script = session.query(ScriptSchedule).get(script_id)
        if script:
            script.last_run = datetime.datetime.utcnow()
            script.next_run = datetime.datetime.utcnow() + datetime.timedelta(minutes=script.frequency)
            session.commit()
        session.close()

    def add_bot(self, name, description):
        session = self.Session()
        new_bot = HomeBot(name=name, description=description)
        session.add(new_bot)
        session.commit()
        bot_id = new_bot.id
        session.close()
        return bot_id

    def get_all_bots(self):
        session = self.Session()
        bots = session.query(HomeBot).all()
        session.close()
        return bots

    def scheduler_daemon(self):
        """Daemon function to run scheduled scripts."""
        scheduler = BackgroundScheduler()
        scheduler.start()

        def check_and_run_scripts():
            due_scripts = self.get_due_scripts()
            for script in due_scripts:
                try:
                    # Execute the script (you might want to customize this part)
                    os.system(f"python {script.script_path}")
                    self.update_script_run_time(script.id)
                except Exception as e:
                    print(f"Error running script {script.script_name}: {e}")

        scheduler.add_job(check_and_run_scripts, 'interval', minutes=1)
        
        try:
            # Keep the scheduler running
            while True:
                pass
        except KeyboardInterrupt:
            scheduler.shutdown()
