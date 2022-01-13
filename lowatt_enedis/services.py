# Copyright (c) 2021 by Lowatt - info@lowatt.fr
#
# This program is part of lowatt_enedis
#
# lowatt_enedis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lowatt_enedis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lowatt_enedis.  If not, see <https://www.gnu.org/licenses/>.
"""
`lowatt_enedis.services`
------------------------

SGE web-service mapping to plug them into the CLI.
"""

from datetime import date, timedelta

from dateutil import tz

from . import (
    arg_from_env,
    create_from_options,
    dict_from_dicts,
    get_option,
    register,
    ws,
)

UTC = tz.tzutc()
ACCORD_CLIENT_OPTIONS = {
    # XXX exclusive option groups
    "--denomination": {
        "help": "Dénomination sociale de la personne morale ayant donné son accord",
    },
    "--nom": {
        "help": "Nom de la personne physique ou nom commerciale de la "
        "personne morale ayant donné son accord",
    },
    "--prenom": {
        "help": "Prénom de la personne physique",
    },
    "--civilite": {
        "choices": ["M", "Mme", "Mlle"],
        "help": "Civilité de la personne physique",
    },
    "--no-autorisation": {
        "action": "store_true",
        "help": "demander sans l'autorisation du client (pour l'homologation seulement)",
    },
}
ACCORD_CLIENT_EXTENDED_OPTIONS = {
    "--naf": {
        "help": "Code NAF de l'activité de la personne morale",
    },
    "--secteur": {
        "help": "Code du secteur d'activité de la personne morale",
    },
    "--siret": {
        "help": "Numéro de SIRET de l'établissement principal de la personne morale",
    },
}

CONTRAT_OPTIONS = {
    "--contrat": dict_from_dicts(
        {
            "help": (
                "identifiant du contrat entre le demandeur et Enedis. "
                "Default to ENEDIS_CONTRAT environment variable."
            ),
        },
        arg_from_env("ENEDIS_CONTRAT"),
    ),
}


def _accord_client(
    client,
    args,
    extended=False,
    xs_accord_type="ns3:DeclarationAccordClientType",
    autorisation=True,
):
    if get_option(args, "denomination"):
        ptype = "Morale"
        who_options = {
            "denomination": "denominationSociale",
        }
        unavailable_options = {"prenom", "civilite"}
        if extended:
            who_options.update(
                {
                    "nom": "nomCommercial",
                    "naf": "activiteCodeNaf",
                    "secteur": "secteurActivite",
                    "siret": "etablissementPrincipalNumSiret",
                },
            )
    elif get_option(args, "nom"):
        ptype = "Physique"
        who_options = {
            "nom": "nom",
            "prenom": "prenom",
            "civilite": "civilite",
        }
        unavailable_options = {"naf", "secteur", "siret"}
    elif extended:  # person info is not mandatory
        ptype = None
    else:
        raise ValueError(
            "You should specify at least one of 'denomination' or 'nom' option",
        )

    accord = client.factory.create(xs_accord_type)

    if hasattr(accord, "accordClient"):
        accord.accordClient = _boolean(autorisation)
    elif hasattr(accord, "accord"):
        # tag name used by CommandeCollectePublicationMesures
        accord.accord = _boolean(autorisation)

    if ptype is not None:
        for option in unavailable_options:
            if getattr(args, option, None):
                raise ValueError(
                    f"L'option {option} ne peut être spécifiée que pour une personne "
                    f"{ptype.lower()}.",
                )

        who = create_from_options(client, args, f"Personne{ptype}Type", who_options)
        setattr(accord, f"personne{ptype}", who)

    return accord


MESURES_OPTIONS = {
    "--from": {
        "default": (date.today() - timedelta(days=1)).isoformat(),
        "help": "date de début souhaitée (incluse)",
    },
    "--to": {
        "default": date.today().isoformat(),
        "help": "date de fin souhaitée (excluse)",
    },
    "--corrigee": {
        "action": "store_true",
        "help": "obtenir les mesures corrigées (C1-C4 uniquement)",
    },
}

MESURES_OPTIONS_MAP = {
    "from": "dateDebut",
    "to": "dateFin",
    "corrigee": "mesuresCorrigees",
}


def _pas(client, args, demande):
    pas = get_option(args, "pas")
    if pas:
        demande.pasCdc = client.factory.create("ns1:DureeType")
        demande.pasCdc.unite = "min"
        demande.pasCdc.valeur = pas


def _check_mesure_options_consistency(args):
    if get_option(args, "pas") and get_option(args, "type") != "CDC":
        raise ValueError(
            "L'option 'pas' ne peut être  spécifiée que pour le type de "
            "mesure 'courbe de charge' (CDC).",
        )


@register(
    "search",
    "RecherchePoint-v2.0",
    {
        "--siret": {
            "help": "n° de siret",
        },
        "--compteur": {
            "help": "matricule ou numéro de série du compteur",
        },
        "--tension": {
            "choices": ["BTINF", "BTSUP", "HTA", "HTB"],
            "help": "domaine de tension d'alimentation",
        },
        "--nom": {
            "help": "nom ou dénomination sociale du client final",
        },
        "--categorie": {
            "choices": ["PRO", "RES"],
            "help": "catégorie de client final",
        },
        "--hp": {
            "action": "store_true",
            "help": "recherche hors-périmetre",
        },
        "--etage": {
            "help": "escalier et étage appartement",
        },
        "--batiment": {
            "help": "batiment",
        },
        "--voie": {
            "help": "numéro et nom de la voie",
        },
        "--lieuDit": {
            "help": "lieu-dit",
        },
        "--cp": {
            "help": "code postal",
        },
        "--insee": {
            "help": "code INSEE de la commune",
        },
    },
)
@ws("RecherchePoint-v2.0")
def search_point(client, args):
    criteria = create_from_options(
        client,
        args,
        "CriteresType",
        {
            "siret": "numSiret",
            "compteur": "matriculeOuNumeroSerie",
            "tension": "domaineTensionAlimentationCode",
            "nom": "nomClientFinalOuDenominationSociale",
            "categorie": "categorieClientFinalCode",
            "hp": "rechercheHorsPerimetre",
        },
    )
    address = create_from_options(
        client,
        args,
        "AdresseInstallationType",
        {
            "etage": "escalierEtEtageEtAppartement",
            "batiment": "batiment",
            "voie": "numeroEtNomVoie",
            "lieuDit": "lieuDit",
            "cp": "codePostal",
            "insee": "codeInseeCommune",
        },
    )
    if address is not None:
        criteria.adresseInstallation = address
    return client.service.rechercherPoint(criteria, get_option(args, "login"))


@register(
    "technical",
    "ConsultationDonneesTechniquesContractuelles-v1.0",
    {
        "prm": {
            "help": "identifiant PRM du point",
        },
        "--autorisation": {
            "help": "indique l'autorisation du client",
            "action": "store_true",
            "default": False,
        },
    },
)
@ws("ConsultationDonneesTechniquesContractuelles-v1.0")
def point_technical_data(client, args):
    return client.service.consulterDonneesTechniquesContractuelles(
        get_option(args, "prm"),
        get_option(args, "login"),
        _boolean(get_option(args, "autorisation")),
    )


@register(
    "measures",
    "ConsultationMesures-v1.1",
    dict_from_dicts(
        {
            "prm": {
                "help": "identifiant PRM du point",
            },
            "--autorisation": {
                "help": "indique l'autorisation du client",
                "action": "store_true",
                "default": False,
            },
        },
        CONTRAT_OPTIONS,
    ),
)
@ws("ConsultationMesures-v1.1")
def point_measures(client, args):
    return client.service.consulterMesures(
        get_option(args, "prm"),
        get_option(args, "login"),
        get_option(args, "contrat"),
        _boolean(get_option(args, "autorisation")),
    )


def parse_date(value):
    return date(*(int(part) for part in value.split("-")))


def measures_resp2py(resp):
    """Return a list of dictionaries given a response from
    ConsultationMesures web-service. Each dict contains the following keys:
    - `grille`: "frn" or "turpe",
    - `grandeurPhysique`: "EA" for active energy,
    - `classeTemporelle`: eg. "BASE", "HP", "HC",
    - `calendrier`: calendar id,
    - `unit`: "kWh",
    - `mesures`: a list of point, each one being a 5-uple with:

      - begin date,
      - end date,
      - value,
      - nature,
      - trigger,
      - status.
    """
    for attr in ("seriesMesuresDateesGrilleTurpe", "seriesMesuresDateesGrilleFrn"):
        try:
            series = getattr(resp, attr).serie
        except AttributeError:
            continue
        grille = attr.split("Grille")[1].lower()
        for serie in series:
            mesures = []
            for point in serie.mesuresDatees.mesure:
                mesures.append(
                    (
                        parse_date(point.dateDebut),
                        parse_date(point.dateFin),
                        int(point.valeur),
                        point.nature._code,
                        point.declencheur._code,
                        point.statut._code,
                    ),
                )
            try:
                calendrier = serie.calendrier._code
            except AttributeError:
                calendrier = None
            yield {
                "grille": grille,
                "grandeurPhysique": serie.grandeurPhysique._code,
                "classeTemporelle": serie.classeTemporelle._code,
                "calendrier": calendrier,
                "unit": serie.unite,
                "mesures": mesures,
            }


@register(
    "details",
    "ConsultationMesuresDetaillees-v2.0",
    dict_from_dicts(
        {
            "prm": {
                "help": "identifiant PRM du point",
            },
            "type": {
                "choices": ["ENERGIE", "PMAX", "COURBE"],
                "help": "type de mesure demandé : ENERGIE pour les consommations "
                "globales quotidiennes, PMAX pour les puissances maximales "
                "quotidiennes, COURBE pour la courbe de charge.",
            },
            "--courbe-type": {
                # - PA pour récupérer les courbes de puissance active (seule
                #   courbe disponible pour les segments C5 et P4)
                # - PRI pour récupérer les courbes de puissance réactive
                #   inductive
                # - PRC pour récupérer les courbes de puissance réactive
                #   capacitive
                # - E pour récupérer les courbes de tension
                # - TOUT pour récupérer les courbes disponibles
                "choices": ["PA", "PRI", "PRC", "E", "TOUT"],
                "default": "PA",
                "help": "type de courbe demandé le cas échéant (Puissance Active, "
                "Puissance Réactive Inductive, Puissance Réactive Capacitive, "
                "tension (E), tout).",
            },
            "--injection": {
                "action": "store_true",
                "help": "demander les données en injection (soutirage par défaut).",
            },
            "--no-autorisation": {
                "action": "store_true",
                "help": "demander sans l'autorisation du client (pour l'homologation seulement)",
            },
        },
        MESURES_OPTIONS,
    ),
)
@ws("ConsultationMesuresDetaillees-v2.0", header_ns_prefix="ns2")
def point_detailed_measures(client, args):
    demande = create_from_options(
        client,
        args,
        "DemandeType",
        dict_from_dicts(
            {
                "login": "initiateurLogin",
                "prm": "pointId",
                "type": "mesuresTypeCode",
            },
            MESURES_OPTIONS_MAP,
        ),
    )
    # demande.mesuresPas uniquement pour PMAX sur C5N, valeur P1D ou P1M
    if get_option(args, "type") == "PMAX":
        demande.grandeurPhysique = "PMA"
        demande.mesuresPas = "P1D"  # 'P1M'
    else:
        del demande.mesuresPas
        if get_option(args, "type") == "ENERGIE":
            demande.grandeurPhysique = "EA"
        elif get_option(args, "type") == "COURBE":
            courbe_type = get_option(args, "courbe_type")
            if not courbe_type:
                raise ValueError(
                    "l'option courbe-type doit être spécifié pour le type de mesure COURBE",
                )
            demande.grandeurPhysique = courbe_type
    injection = get_option(args, "injection")
    demande.soutirage = _boolean(not injection)
    demande.injection = _boolean(injection)
    demande.accordClient = _boolean(not get_option(args, "no_autorisation"))

    return client.service.consulterMesuresDetaillees(demande)


def detailed_measures_resp2py(resp):
    """Return an iterator on (UTC tz naive datetime, value) given a response from
    ConsultationMesuresDetaillees web-service.
    """
    # start = resp.periode.dateDebut
    # end = resp.periode.dateFin
    assert len(resp.grandeur) == 1
    for point in resp.grandeur[0].mesure:
        yield (point.d.astimezone(UTC), point.v)


def _donnees_generales(
    client,
    args,
    code,
    tag_name,
):
    obj = create_from_options(
        client,
        args,
        tag_name,
        {
            # XXX missing: refFrn, refFrnRegroupement, affaireLieeId
            "contrat": "contratId",
            "prm": "pointId",
            "login": "initiateurLogin",
        },
    )
    obj.objetCode = code
    return obj


DONNEES_GENERALES_OPTIONS = dict_from_dicts(
    {
        "prm": {
            "help": "identifiant PRM du point",
        },
    },
    CONTRAT_OPTIONS,
)


@register(
    "cmdHisto",
    "CommandeTransmissionHistoriqueMesures-v1.0",
    dict_from_dicts(
        DONNEES_GENERALES_OPTIONS,
        {
            "type": {
                "choices": ["IDX", "CDC"],
                "help": "type de mesure demandé : IDX pour les index, CDC pour la "
                "courbe de charge.",
            },
            "--pas": {
                "choices": ["10", "30"],
                "help": "pas souhaité dans le cas des courbes de charges ; "
                "10 pour C1-C4 / 30 pour C5",
            },
        },
        ACCORD_CLIENT_OPTIONS,
        ACCORD_CLIENT_EXTENDED_OPTIONS,
        MESURES_OPTIONS,
        {
            # override --from's default to 2 years
            "--from": {
                "default": (date.today() - timedelta(days=365 * 2)).isoformat(),
                "help": "date de début souhaitée",
            },
        },
    ),
)
@ws("CommandeTransmissionHistoriqueMesures-v1.0", header_ns_prefix="ns1")
def point_cmd_histo(client, args):
    _check_mesure_options_consistency(args)

    header = client.options.soapheaders
    header.infoFonctionnelles = client.factory.create("ns1:infoFonctionnelles")
    header.infoFonctionnelles.pointId = get_option(args, "prm")
    del header.infoFonctionnelles.affaireId

    demande = client.factory.create("ns0:HistoriqueMesuresDemandeType")

    demande.donneesGenerales = _donnees_generales(
        client,
        args,
        "HDM",
        "DemandeDonneesGeneralesType",
    )

    demande.historiqueMesures = create_from_options(
        client,
        args,
        "DemandeHistoriqueMesuresType",
        dict_from_dicts(
            MESURES_OPTIONS_MAP,
            {
                "type": "mesureType",
                "corrigee": "mesureCorrigee",  # override mesuresCorrigees
            },
        ),
    )
    _pas(client, args, demande.historiqueMesures)
    demande.historiqueMesures.declarationAccordClient = _accord_client(
        client,
        args,
        True,
        "ns0:DeclarationConsentementType",
    )

    return client.service.commanderTransmissionHistoriqueMesures(demande)


@register(
    "cmdInfraJ",
    "CommandeTransmissionDonneesInfraJ-v1.0",
    dict_from_dicts(
        DONNEES_GENERALES_OPTIONS,
        {
            "--injection": {
                "action": "store_true",
                "help": "demander les données en injection (courbe de charge, "
                "tension et index).",
            },
            "--soutirage": {
                "action": "store_true",
                "help": "demander les données en soutirage (courbe de charge, "
                "tension et index et paramètres de tarification dynamique).",
            },
            "--cdc": {
                "action": "store_true",
                "help": "demander les données les courbes de charge et de tension.",
            },
            "--idx": {
                "action": "store_true",
                "help": "demander les données les données d'index.",
            },
            "--ptd": {
                "action": "store_true",
                "help": "demander les paramètres de tarification dynamique.",
            },
        },
        ACCORD_CLIENT_OPTIONS,
    ),
)
@ws("CommandeTransmissionDonneesInfraJ-v1.0")
def point_cmd_infra_j(client, args):
    demande = client.factory.create("ns1:DemandeType")

    demande.donneesGenerales = _donnees_generales(
        client,
        args,
        "AME",
        "DonneesGeneralesType",
    )

    demande.accesDonnees = create_from_options(
        client,
        args,
        "DemandeAccesDonneesType",
        {
            "injection": "injection",
            "soutirage": "soutirage",
            "cdc": "cdc",
            "idx": "idx",
            "ptd": "ptd",
        },
    )
    demande.accesDonnees.declarationAccordClient = accord = _accord_client(
        client,
        args,
        xs_accord_type="ns1:DeclarationAccordClientType",
        autorisation=not get_option(args, "no_autorisation"),
    )
    accord.injection = _boolean(False)
    accord.soutirage = _boolean(False)
    return client.service.commanderTransmissionDonneesInfraJ(demande)


@register(
    "subscribe",
    "CommandeCollectePublicationMesures-v3.0",
    dict_from_dicts(
        DONNEES_GENERALES_OPTIONS,
        {
            "--cdc-enable": {
                "action": "store_true",
                "help": "demander la collecte de la courbe de charge.",
            },
            "--cdc": {
                "action": "store_true",
                "help": "demander la transmission données les courbes de charge.",
            },
            "--idx": {
                "action": "store_true",
                "help": "demander la transmission des données d'index index et autres "
                "données du compteur.",
            },
            "--period": {
                "choices": ["daily", "weekly", "monthly"],
                "default": "daily",
                "help": "périodicité de réception pour la courbe de charge "
                "(quotidienne par défaut).",
            },
            "--injection": {
                "action": "store_true",
                "help": "demander les données en injection (soutirage par défaut).",
            },
            "--linky": {
                "action": "store_true",
                "help": "la demande concerne le segment C5 ou P4"
                "(segment C1-C4 ou P1-P3 par défaut).",
            },
        },
        ACCORD_CLIENT_OPTIONS,
        MESURES_OPTIONS,
        {
            # override --from --to
            "--from": {
                "default": date.today().isoformat(),
                "help": "date de début, postérieure ou égale à la date du jour",
            },
            "--to": {
                "default": (date.today() + timedelta(days=365)).isoformat(),
                "help": "date de fin souhaitée, "
                "supérieure à la date de fin précédente lors d’un renouvellement, "
                "un an max pour les compteurs linky",
            },
        },
    ),
)
@ws("CommandeCollectePublicationMesures-v3.0")
def point_cmd_publication(client, args):
    demande = client.factory.create("ns1:DemandeType")

    demande.donneesGenerales = _donnees_generales(
        client,
        args,
        "AME",
        "DonneesGeneralesType",
    )

    demande.accesMesures = acces = create_from_options(
        client,
        args,
        "DemandeAccesMesures",
        dict_from_dicts(MESURES_OPTIONS_MAP),
    )

    supported_actions = ["cdc_enable", "cdc", "idx"]
    action = [a for a in supported_actions if get_option(args, a)]

    if not action or len(action) > 1:
        raise ValueError(f"Une action doit être selectionnée parmi {supported_actions}")

    action = action[0]

    if action == "idx":
        code = "IDX"
        transmission = True
        pas = "P1D"
        period = "P1D"
    else:
        code = "CDC"
        transmission = action == "cdc"
        if get_option(args, "linky"):
            pas = "PT30M"
        else:
            pas = "PT10M"
        period = get_option(args, "period")
        if period == "monthly":
            period = "P1M"
        elif period == "weekly":
            period = "P7D"
        else:
            period = "P1D"

    injection = get_option(args, "injection")

    acces.mesuresTypeCode = code
    acces.transmissionRecurrente = _boolean(transmission)
    acces.mesuresPas = pas
    acces.periodiciteTransmission = period
    acces.injection = _boolean(injection)
    acces.soutirage = _boolean(not injection)

    if injection and get_option(args, "linky"):
        del demande.periodiciteTransmission

    demande.accesMesures.declarationAccordClient = _accord_client(
        client,
        args,
        xs_accord_type="ns1:DeclarationAccordClientType",
        autorisation=not get_option(args, "no_autorisation"),
    )

    return client.service.commanderCollectePublicationMesures(demande)


@register(
    "subscriptions",
    "RechercherServicesSouscritsMesures-v1.0",
    DONNEES_GENERALES_OPTIONS,
)
@ws("RechercherServicesSouscritsMesures-v1.0")
def point_search_subscriptions(client, args):
    criteria = create_from_options(
        client,
        args,
        "CriteresType",
        {
            "contrat": "contratId",
            "prm": "pointId",
        },
    )

    return client.service.rechercherServicesSouscritsMesures(
        criteria,
        get_option(args, "login"),
    )


@register(
    "unsubscribe",
    "CommandeArretServiceSouscritMesures-v1.0",
    dict_from_dicts(
        DONNEES_GENERALES_OPTIONS,
        {
            "--id": {
                "help": "identifiant du service souscrit de mesures à arrêter",
            },
        },
    ),
)
@ws("CommandeArretServiceSouscritMesures-v1.0")
def point_unsubscribe(client, args):
    demande = client.factory.create("ns1:DemandeType")

    demande.donneesGenerales = _donnees_generales(
        client,
        args,
        "ASS",
        "DonneesGeneralesType",
    )

    demande.arretServiceSouscrit = create_from_options(
        client,
        args,
        "ArretServiceSouscritType",
        {"id": "serviceSouscritId"},
    )

    return client.service.commanderArretServiceSouscritMesures(demande)


def _boolean(b):
    return "true" if b else "false"
