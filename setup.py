from setuptools import setup

setup(
    entry_points={
        'trac.plugins': [
            "ticket-reporter = twisted_trac_plugins.ticket_reporter",
            "ticket-emailer = twisted_trac_plugins.ticket_emailer",
            "user-database = twisted_trac_plugins.user_database",
            ],
        },
    name='Twisted Trac Plugins', version='0.0',
    description="Plugins for twisted's trac instance",
    author="Tom Prince", author_email="tomprince@twistedmatrix.com",
    license='MIT',
    url='https://github.com/twisted-infra/twisted-trac-plugins',
    packages=['twisted_trac_plugins', 'twisted_trac_plugins.user_database'],
    package_data={'twisted_trac_plugins.user_database': ['templates/*']},
)
