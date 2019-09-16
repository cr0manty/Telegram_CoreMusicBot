from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

from bot import StartBot
from config import TOKEN
from config import Configuration

server = Flask(__name__)
server.config.from_object(Configuration)
db = SQLAlchemy(server)

bot = StartBot(server, TOKEN, debug=True)

migrate = Migrate(server, db)
manager = Manager(server)
manager.add_command('db', MigrateCommand)
