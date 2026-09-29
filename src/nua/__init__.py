from nua import api, config, db, domain, services
from nua.bootstrap import Bootstrapper
from nua.root_container import RootContainer


def main():
    container = RootContainer()
    bootstrapper = Bootstrapper(container)

    bootstrapper.run()


__all__ = [
    'RootContainer',
    'Bootstrapper',
    'config',
    'api',

    'db',
    'domain',
    'services',

    'main'
]
