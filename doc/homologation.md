Homologation
============

This explain how to pass through Enedis homologation process.

This is based on SGE v23.4 (from `Enedis.SGE.REF.0465.Homologation_Catalogue
des cas de tests_Tiers_SGE23.4_v1.0.pdf`) cases.

First setup `lowatt-enedis` and then execute given commands for each services
you want homologation and report the time the command was run to fill Enedis
excel file.

Setup
-----

Set these environment variables to setup `lowatt-enedis`:

```
$ export ENEDIS_KEY_FILE=/path/to/key.pem
$ export ENEDIS_CERT_FILE=/path/to/cert.pem
$ export ENEDIS_LOGIN=XXX
$ export ENEDIS_CONTRAT=XXX
$ export ENEDIS_HOMOLOGATION=on
```

ConsultationDonneesTechniquesContractuelles v1.0
------------------------------------------------

| Case           | Command                                                 |
|----------------|---------------------------------------------------------|
| ADP-R1 (C1-C4) | `lowatt-enedis technical --autorisation 98800007059999` |
| ADP-R1 (C5)    | `lowatt-enedis technical --autorisation 25946599093143` |
| ADP-R2 (C1-C4) | `lowatt-enedis technical 98800007059999`                |
| ADP-R2 (C5)    | `lowatt-enedis technical 25946599093143`                |
| ADP-NR1        | `lowatt-enedis technical 99999999999999`                |

ConsultationMesures v1.1
------------------------

| Case              | Command                                                 |
|-------------------|---------------------------------------------------------|
| AHC-R1 (C1-C4) \* | `lowatt-enedis measures --autorisation 30001610071843`  |
| AHC-R1 (C5)       | `lowatt-enedis measures --autorisation 25957452924301`  |
| AHC-NR1           | `lowatt-enedis measures 30001610071843`                 |

\* Returned "SGT4G3: Aucune mesure trouvée pour ce PRM" on the homologation environment v23.2

ConsultationMesuresDetaillees v3.0
----------------------------------

| Case               | Command                                                                                                  |
|--------------------|----------------------------------------------------------------------------------------------------------|
| CMD3-R1 (C1-C4)    | `lowatt-enedis detailsV3 30001610071843 COURBE --from 2022-04-01 --to 2022-04-07`                        |
| CMD3-R1 (C5)       | `lowatt-enedis detailsV3 25478147557460 COURBE --from 2022-04-01 --to 2022-04-07`                        |
| CMD3-R2            | `lowatt-enedis detailsV3 30001610071843 COURBE --courbe-type PRI --from 2022-04-01 --to 2022-04-07`      |
| CMD3-R3 (C1-C4) \* | `lowatt-enedis detailsV3 30001610071843 ENERGIE --from 2022-04-01 --to 2022-04-07`                       |
| CMD3-R3 (C5)       | `lowatt-enedis detailsV3 25478147557460 ENERGIE --from 2022-04-01 --to 2022-04-07`                       |
| CMD3-R4            | `lowatt-enedis detailsV3 25478147557460 PMAX --from 2022-04-01 --to 2022-04-07`                          |
| CMD3-R5 (C1-C4) \* | `lowatt-enedis detailsV3 30001610071843 INDEX --from 2022-04-01 --to 2022-04-07`                         |
| CMD3-R5 (C5) \*    | `lowatt-enedis detailsV3 25478147557460 INDEX --from 2022-04-01 --to 2022-04-07`                         |
| CMD3-R6 (C1-C4) \* | `lowatt-enedis detailsV3 30001610071843 INDEX --from 2022-04-01 --to 2022-04-07 --cadre SERVICE_ACCES`   |
| CMD3-R6 (C5) \*    | `lowatt-enedis detailsV3 25478147557460 INDEX --from 2022-04-01 --to 2022-04-07 --cadre SERVICE_ACCES`   |
| CMD3-NR1           | `lowatt-enedis detailsV3 25478147557460 COURBE --from 2022-04-01 --to 2022-04-17`                        |
| CMD3-NR2 \*        | `lowatt-enedis detailsV3 25478147557460 INDEX --from 2022-04-01 --to 2022-04-17 --cadre SERVICE_ACCES`   |

\* Returned "SGT4G3: Aucune mesure trouvée pour ce PRM" on the homologation environment v23.2

RecherchePoint v2.0
-------------------

| Case     | Command                                                                                           |
|----------|---------------------------------------------------------------------------------------------------|
| RP-R1    | `lowatt-enedis search --tension BTINF --categorie RES --cp 34650 --insee 34231`                   |
| RP-R2 \* | `lowatt-enedis search --voie "1 RUE DE LA MER" --nom=TEST --cp 84160 --insee 84042 --hp`          |
| RP-R3 \* | `lowatt-enedis search --voie "1 RUE DE LA MER" --nom=TES --cp 84160 --insee 84042 --hp`           |
| RP-NR1   | `lowatt-enedis search --categorie RES --cp 84160 --insee 84042`                                   |
| RP-NR2   | `lowatt-enedis search --insee 34231 --voie "1 RUE DE LA MER"`                                     |

\* Returned "None" on the homologation environment v23.2

CommandeAccesDonneesMesures v1.0
---------------------------------

| Case                | Command                                                                        |
|---------------------|--------------------------------------------------------------------------------|
| ACCES-R1 (C5) \*\*  | `lowatt-enedis cmdAcces 24380318190106 ENERGIE --nom DUPONT`                   |
| ACCES-R1 (C2-C4) \* | `lowatt-enedis cmdAcces 98800005569823 ENERGIE --nom DUPONT`                   |
| ACCES-R2 (C5) \*\*  | `lowatt-enedis cmdAcces 24380318190106 COURBE --nom DUPONT`                    |
| ACCES-R2 (C2-C4) \* | `lowatt-enedis cmdAcces 98800005569823 COURBE --nom DUPONT`                    |
| ACCES-R3 \*\*       | `lowatt-enedis cmdAcces 24380318190106 PMAX --nom DUPONT`                      |
| ACCES-R4 (C5) \*\*  | `lowatt-enedis cmdAcces 24380318190106 INDEX --nom DUPONT`                     |
| ACCES-R4 (C2-C4) \* | `lowatt-enedis cmdAcces 98800005569823 INDEX --nom DUPONT`                     |
| ACCES-NR1 (C5)      | `lowatt-enedis cmdAcces 24380318190106 ENERGIE --nom DUPONT --no-autorisation` |
| ACCES-NR1 (C2-C4)   | `lowatt-enedis cmdAcces 98800005569823 ENERGIE --nom DUPONT --no-autorisation` |
| ACCES-NR2 (C5)      | `lowatt-enedis cmdAcces 24380318190106 ENERGIE --nom DUPONT --to 2050-04-21`   |
| ACCES-NR2 (C2-C4)   | `lowatt-enedis cmdAcces 98800005569823 ENERGIE --nom DUPONT --to 2050-04-21`   |

\* Returned "SGT400: Une erreur fonctionnelle est survenue." on the homologation environment v23.2

\*\* Returned "SGT4B8: Il existe déjà plusieurs demandes en cours sur le point." on the homologation environment v23.2

CommandeCollectePublicationMesures v3.0
---------------------------------------

**This webservice does not work on the C2-C4 segment in the Homologation environment.**

> Le webservice CommandeCollectePublicationMesures ne fonctionne pas sur le segment C2-C4 dans l’environnement d’Homologation.
> L’acteur tiers sera donc homologué sur la requête pour le segment C2-C4.
> Il ne devra pas prêter attention à la réponse qui lui sera renvoyée via webservice.

| Case        | Command                                                                                                                |
|-------------|------------------------------------------------------------------------------------------------------------------------|
| F300C_O1    | `lowatt-enedis subscribe 25884515170669 --cdc --linky --denomination "COGIP"`                                          |
| F300B_O1 \* | `lowatt-enedis subscribe 98800000000246 --cdc --denomination "COGIP"`                                                  |
| F300C_O2    | `lowatt-enedis subscribe 25884515170669 --cdc-enable --linky --denomination "COGIP"`                                   |
| F300B_O2 \* | `lowatt-enedis subscribe 98800000000246 --cdc-enable --denomination "COGIP"`                                           |
| F305        | `lowatt-enedis subscribe 25884515170669 --idx --denomination "COGIP"`                                                  |
| F305A    \* | `lowatt-enedis subscribe 98800000000246 --idx --denomination "COGIP"`                                                  |
| F305C       | `lowatt-enedis subscribe 25884515170669 --idx --denomination "COGIP"`                                                  |
| F300C_O1-NR | `lowatt-enedis subscribe 25884515170669 --cdc --linky --to 2100-01-01 --denomination "COGIP"`                          |
| F300C_O2-NR | `lowatt-enedis subscribe 25884515170669 --cdc-enable --linky --denomination "COGIP" --no-autorisation`                 |
| F300B_O2-NR | `lowatt-enedis subscribe 98800000000246 --cdc-enable --linky --denomination "COGIP" --no-autorisation`                 |
| F305-NR     | `lowatt-enedis subscribe 25884515170669 --idx --denomination "COGIP" --no-autorisation`                                |
| F305A-NR    | `lowatt-enedis subscribe 98800000000246 --idx --denomination "COGIP" --no-autorisation`                                |

\* Returned "SGT400: Une erreur fonctionnelle est survenue." on the homologation environment v23.2

RechercherServicesSouscritsMesures v1.0
---------------------------------------

**This webservice does not work on the C2-C4 segment in the Homologation environment.**

> Le webservice RechercheServicesSouscritsMesures v1.0 ne fonctionne pas sur le segment C2-C4 dans l’environnement d’Homologation.
> L’acteur tiers sera donc homologué sur la requête pour le segment C2-C4.
> Il ne devra pas prêter attention à la réponse qui lui sera renvoyée via webservice.

| Case             | Command                                      |
|------------------|----------------------------------------------|
| RS-R1 (C5)       | `lowatt-enedis subscriptions 25884515170669` |
| RS-R1 (C2-C4) \* | `lowatt-enedis subscriptions 98800000000246` |

\* Returned "None" on the homologation environment v23.2

CommandeArretServiceSouscritMesures v1.0
----------------------------------------

**This webservice does not work on the C2-C4 segment in the Homologation environment.**

> Le webservice CommandeArretServiceSouscritMesures v1.0 ne fonctionne pas sur le segment C2-C4 dans l’environnement d’Homologation.
> L’acteur tiers sera donc homologué sur la requête pour le segment C2-C4.
> Il ne devra pas prêter attention à la réponse qui lui sera renvoyée via webservice.

| Case                   | Command                                                  |
|------------------------|----------------------------------------------------------|
| ASS-R1 (C5) \*\*       | `lowatt-enedis unsubscribe 25884515170669 --id 47761068` |
| ASS-R1 (C2-C4) \* \*\* | `lowatt-enedis unsubscribe 98800000000246 --id 47761068` |

\* Returned "SGT500: Une erreur technique est survenue" on the homologation environment v23.2

\*\* Use an id returned by RS-R1.

CommandeTransmissionDonneesInfraJ v1.0
--------------------------------------

**This webservice does not work in the Homologation environment.**

> Le webservice CommandeTransmissionDonneesInfraJ ne fonctionne pas dans l’environnement d’Homologation.
> L’acteur tiers sera donc homologué sur les requêtes.
> Il ne devra pas prêter attention aux réponses qui lui seront renvoyées via webservice.

| Case         | Command                                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------------------|
| F375A-R1 \*  | `lowatt-enedis cmdInfraJ 98800000000246 --cdc --soutirage --denomination "Raison Sociale"`                           |
| F375A-NR1 \* | `lowatt-enedis cmdInfraJ 98800000000246 --idx --injection --denomination "Raison Sociale" --no-autorisation`         |

\* Returned "SGT500: Une erreur technique est survenue" on the homologation environment v23.2

CommandeHistoriqueDonneesMesuresFines v1.0
------------------------------------------

**This webservice does not work in the Homologation environment.**

| Case                   | Command                                                                                                                           |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| MFI-GK-R1 (C5) \*      | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 ENERGIE`                   |
| MFI-GK-R1 (C2-C4) \*   | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 ENERGIE`                   |
| MFI-GK-R2 (C5) \*      | `lowatt-enedis cmdHistoFine 25150217034354 COURBES`                                                                               |
| MFI-GK-R2 (C2-C4) \*   | `lowatt-enedis cmdHistoFine 98800004935121 COURBES`                                                                               |
| MFI-GK-R3 (C5) \*      | `lowatt-enedis cmdHistoFine 25150217034354 PMAX`                                                                                  |
| MFI-GK-R3 (C2-C4) \*   | `lowatt-enedis cmdHistoFine 98800004935121 PMAX`                                                                                  |
| MFI-GK-R4 (C5) \*      | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 INDEX`                     |
| MFI-GK-R4 (C2-C4) \*   | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 INDEX`                     |
| MFI-GK-NR1 (C5) \*     | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 COURBES --from 2020-01-01` |
| MFI-GK-NR1 (C2-C4) \*  | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 COURBES`                   |
| MFI-GK-NR2 (C5) \*     | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 INDEX --from 2020-01-01`   |
| MFI-GK-NR2 (C2-C4) \*  | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 INDEX`                     |

\* Returned "Erreur Technique MFI v23.4

CommandeHistoriqueDonneesMesuresFacturantes v1.0
------------------------------------------------

**This webservice does not work in the Homologation environment.**

| Case                   | Command                                                                                                                                   |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| MFA-GK-R1 (C5) \*      | `lowatt-enedis cmdHistoFact 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289`                                   |
| MFA-GK-R1 (C2-C4) \*   | `lowatt-enedis cmdHistoFact 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186`                                   |
| MFA-GK-NR1 (C5) \*     | `lowatt-enedis cmdHistoFact 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 --from 2023-10-01 --to 2023-08-01` |
| MFA-GK-NR1 (C2-C4) \*  | `lowatt-enedis cmdHistoFact 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186  --from 2023-10-01 --to 2023-08-01`|

\* Returned "Erreur Technique MFA v23.4

CommandeInformationsTechniquesEtContractuelles v1.0
---------------------------------------------------

**This webservice does not work in the Homologation environment.**

| Case                   | Command                                                                                                 |
|------------------------|---------------------------------------------------------------------------------------------------------|
| ITC-GK-R1 (C5) \*      | `lowatt-enedis cmdTechnical 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289` |
| ITC-GK-R1 (C2-C4) \*   | `lowatt-enedis cmdTechnical 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186` |

\* Returned "Erreur Technique ITC v23.4
