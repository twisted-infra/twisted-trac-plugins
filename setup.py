from setuptools import setup

setup(
    entry_points={
        'trac.plugins': [
            "ticket-reporter = twisted_trac_plugins.ticket_reporter",
            "ticket-emailer = twisted_trac_plugins.ticket_emailer",
            ],
        },
    name='Twisted Trac Plugins', version='0.0',
    description="Plugins for twisted's trac instance",
    author="Tom Prince", author_email="tomprince@twistedmatrix.com",
    license='MIT',
    url='https://github.com/twisted-infra/twisted-trac-plugins',
    packages=['twisted_trac_plugins'],
)
