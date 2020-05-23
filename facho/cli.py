import sys
import click

import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

@click.command()
@click.option('--nit', required=True)
@click.option('--nit-proveedor', required=True)
@click.option('--id-software', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
def consultaResolucionesFacturacion(nit, nit_proveedor, id_software, username, password):
    from facho.fe.client import dian
    client_dian = dian.DianClient(username,
                                  password)
    resp = client_dian.request(dian.ConsultaResolucionesFacturacionPeticion(
        nit, nit_proveedor, id_software
    ))
    print(str(resp))


@click.group()
def main():
    pass

main.add_command(consultaResolucionesFacturacion)
