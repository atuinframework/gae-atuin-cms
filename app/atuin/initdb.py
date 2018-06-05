# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.curdir)
import time
import datetime
import random
import csv
import re
import pprint

from handler import app
from datastore import db

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from atuin.auth.models import *
from atuin.logs.models import *

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def create_admin():
    print "Creating admin..."

    u = User(usertype="staff", username="admin", name="Admin", role="ADMIN")
    u.set_password('admin')
    db.session.add(u)

    db.session.commit()


@manager.command
def create_demo_users():
    print "Deleting demo users..."

    db.session.commit()


@manager.command
def update_policies():
    print "Updating policies..."

    UserPolicy.query.delete()

    db.session.add(UserPolicy(desc="User", role='USER', functions=','.join([
        "FUNC1", "FUNC2"
    ])))

    db.session.commit()


@manager.command
def create_demo_data():
    print("Deleting demo data...")


if __name__ == '__main__':
    manager.run()
