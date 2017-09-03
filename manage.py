#!/usr/bin/env python
import os
from nba import create_app, db

# import all relevant models from models.py
from nba.models import User, Series, Prediction,calculate_score
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('production')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
	# add all imported models to dict
    return dict(app=app, db=db, User=User, Series = Series,
    	Prediction=Prediction, calculate_score = calculate_score)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
