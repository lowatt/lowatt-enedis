# lowatt-enedis

A command-line tool and Python library to access
[Enedis](https://www.enedis.fr/) SGE SOAP web-services, provided by
[LOWATT](https://www.lowatt.fr).

Disclaimer: this package is *NOT* affiliated to Enedis, but provided by Lowatt
in case it could be useful to other users of the SGE web-services provided by
Enedis.

## Licensing

It is published under the terms of the GPL 3 license.

## Installation

``pip install lowatt-enedis``

## Command line usage

See ``lowatt-enedis --help`` for CLI usage. You'll be able to call the services
controlled using options and see the SOAP response.  You can take a look at
``doc/homologation.md`` for a sample session to go through Enedis'homologation
process.

Some flags are required by all or most of the commands so they can be
configured once by their respective environment variables.

| Option        | Environment variable |
|---------------|----------------------|
| `--cert-file` | `ENEDIS_CERT_FILE`   |
| `--key-file`  | `ENEDIS_KEY_FILE`    |
| `--login`     | `ENEDIS_LOGIN`       |
| `--contrat`   | `ENEDIS_CONTRAT`     |

## Python library usage

Here is a sample code to access to the ``ConsultationMesuresDetaillees`` from
Python code :

```python
import datetime
import lowatt_enedis
import lowatt_enedis.services

config = {
    'login': 'you@example.com',
    'certificateFile': 'fullchain.pem',
    'keyFile': 'privkey.pem',
    'prm': '30000123456789',
}
# get client for the 'details' service using appropriate client
# certificate and key
client = lowatt_enedis.get_client(
    lowatt_enedis.COMMAND_SERVICE['details'][0],
    config['certificateFile'], config['keyFile'],
)
# actually call the web to get values for the past week
resp = lowatt_enedis.services.point_detailed_measures(client, {
    'login': config['login'],
    'prm': config['prm'],
    'type': 'COURBE',
    'courbe_type': 'PA',
    'corrigee': True,
    'from': datetime.date.today() - datetime.timedelta(days=7),
    'to': datetime.date.today(),
})
# get a list of (UTC timestamp, value(W))
data = lowatt_enedis.services.measures_resp2py(resp)
```

## Contributions

Contribution are welcome through the [Github
repository](https://github.com/lowatt/lowatt_enedis).

Feel free to contact for more info by writing at info@lowatt.fr.

## Sponsors

[![QosEnergy](assets/qos-energy.png)](https://www.qosenergy.com/)
