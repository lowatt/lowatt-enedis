Homologation
============

This explain how to pass through Enedis homologation process.

This is based on SGE v26.1 (from `Enedis.SGE.REF.0465.Homologation_Catalogue des cas de tests_Tiers_SGE26.1.pdf`) cases.

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
| ADP-R1 (C1-C4) | `lowatt-enedis technical --autorisation 98800004847471` |
| ADP-R1 (C5)    | `lowatt-enedis technical --autorisation 25946599093143` |
| ADP-R2 (C1-C4) | `lowatt-enedis technical 98800004847471`                |
| ADP-R2 (C5)    | `lowatt-enedis technical 25946599093143`                |
| ADP-NR1        | `lowatt-enedis technical 99999999999999`                |

ConsultationMesures v1.1
------------------------

| Case              | Command                                                 |
|-------------------|---------------------------------------------------------|
| AHC-R1 (C1-C4)    | `lowatt-enedis measures --autorisation 98800000396971`  |
| AHC-R1 (C5)       | `lowatt-enedis measures --autorisation 25162373298976`  |
| AHC-NR1           | `lowatt-enedis measures 25162373298976`                 |

ConsultationMesuresDetaillees v3.0
----------------------------------

| Case               | Command                                                                                                  |
|--------------------|----------------------------------------------------------------------------------------------------------|
| CMD3-R1 (C1-C4)    | `lowatt-enedis detailsV3 98800001144455 COURBE --from 2025-04-01 --to 2025-04-07`                        |
| CMD3-R1 (C5)       | `lowatt-enedis detailsV3 25162373298976 COURBE --from 2025-04-01 --to 2025-04-07`                        |
| CMD3-R2            | `lowatt-enedis detailsV3 98800001144455 COURBE --courbe-type PRI --from 2025-04-01 --to 2025-04-07`      |
| CMD3-R3 (C1-C4)    | `lowatt-enedis detailsV3 98800001144455 ENERGIE --from 2024-03-15 --to 2025-07-23`                       |
| CMD3-R3 (C5)       | `lowatt-enedis detailsV3 25162373298976 ENERGIE --from 2025-04-01 --to 2025-04-07`                       |
| CMD3-R4            | `lowatt-enedis detailsV3 25162373298976 PMAX --from 2025-04-01 --to 2025-04-07`                          |
| CMD3-R5 (C1-C4)    | `lowatt-enedis detailsV3 98800001144455 INDEX --from 2024-03-15 --to 2025-07-23`                         |
| CMD3-R5 (C5)       | `lowatt-enedis detailsV3 25162373298976 INDEX --from 2025-04-01 --to 2025-04-07`                         |
| CMD3-R6 (C1-C4)    | `lowatt-enedis detailsV3 98800001144455 INDEX --from 2024-03-15 --to 2025-07-23 --cadre SERVICE_ACCES`   |
| CMD3-R6 (C5)       | `lowatt-enedis detailsV3 25162373298976 INDEX --from 2025-04-01 --to 2025-04-07 --cadre SERVICE_ACCES`   |
| CMD3-NR1           | `lowatt-enedis detailsV3 25162373298976 COURBE --from 2025-04-01 --to 2025-04-07`                        |
| CMD3-NR2           | `lowatt-enedis detailsV3 25162373298976 INDEX --from 2025-04-01 --to 2025-04-07 --cadre SERVICE_ACCES`   |

RecherchePoint v2.0
-------------------

| Case     | Command                                                                                           |
|----------|---------------------------------------------------------------------------------------------------|
| RP-R1    | `lowatt-enedis search --tension BTINF --categorie RES --cp 34650 --insee 34231`                   |
| RP-R2    | `lowatt-enedis search --voie "1 RUE DE LA MER" --nom=TEST --cp 84160 --insee 84042 --hp`          |
| RP-R3    | `lowatt-enedis search --voie "1 RUE DE LA MER" --nom=TES --cp 84160 --insee 84042 --hp`           |
| RP-NR1   | `lowatt-enedis search --categorie RES --cp 84160 --insee 84042`                                   |
| RP-NR2   | `lowatt-enedis search --insee 34231 --voie "1 RUE DE LA MER"`                                     |

CommandeAccesDonneesMesures v1.0
---------------------------------

| Case                | Command                                                                        |
|---------------------|--------------------------------------------------------------------------------|
| ACCES-R1 (C5)       | `lowatt-enedis cmdAcces 24380318190106 ENERGIE --nom DUPONT`                   |
| ACCES-R1 (C2-C4)    | `lowatt-enedis cmdAcces 98800003605600 ENERGIE --nom DUPONT`                   |
| ACCES-R2 (C5)       | `lowatt-enedis cmdAcces 24380318190106 COURBE --nom DUPONT`                    |
| ACCES-R2 (C2-C4)    | `lowatt-enedis cmdAcces 98800003605600 COURBE --nom DUPONT`                    |
| ACCES-R3            | `lowatt-enedis cmdAcces 24380318190106 PMAX --nom DUPONT`                      |
| ACCES-R4 (C5)       | `lowatt-enedis cmdAcces 24380318190106 INDEX --nom DUPONT`                     |
| ACCES-R4 (C2-C4)    | `lowatt-enedis cmdAcces 98800003605600 INDEX --nom DUPONT`                     |
| ACCES-NR1 (C5)      | `lowatt-enedis cmdAcces 24380318190106 ENERGIE --nom DUPONT --no-autorisation` |
| ACCES-NR1 (C2-C4)   | `lowatt-enedis cmdAcces 98800003605600 ENERGIE --nom DUPONT --no-autorisation` |
| ACCES-NR2 (C5)      | `lowatt-enedis cmdAcces 24380318190106 ENERGIE --nom DUPONT --to 2050-04-21`   |
| ACCES-NR2 (C2-C4)   | `lowatt-enedis cmdAcces 98800003605600 ENERGIE --nom DUPONT --to 2050-04-21`   |

CommandeArretServicesAccesDonnees v1.0
--------------------------------------

| Case               | Command                                                                        |
|--------------------|--------------------------------------------------------------------------------|
| ASAD-R1 (C5)       | `lowatt-enedis cmdArretServiceAccesDonnees 24380318190106 --service-id 666`    |
| ASAD-R1 (C2-C4)    | `lowatt-enedis cmdArretServiceAccesDonnees 98800003605600 --service-id 666`    |

CommandeModificationOptionsServicesAccesDonnees v1.0
----------------------------------------------------

| Case              | Command                                                                                                                            |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------|
| MOSAD-R1 (C5)     | `lowatt-enedis cmdModificationOptionsServicesAccesDonnees 24377424002398 --service-id 666 --add-period daily --add-corrigee`    |
| MOSAD-R1 (C2-C4)  | `lowatt-enedis cmdModificationOptionsServicesAccesDonnees 98800003605600 --service-id 666 --add-period daily --add-corrigee`    |
| MOSAD-R2 (C5)     | `lowatt-enedis cmdModificationOptionsServicesAccesDonnees 24377424002398 --service-id 666 --drop-period daily --drop-corrigee`  |
| MOSAD-R2 (C2-C4)  | `lowatt-enedis cmdModificationOptionsServicesAccesDonnees 98800003605600 --service-id 666 --drop-period daily --drop-corrigee`  |

CommandeServicesAccesDonnees v1.0
---------------------------------

| Case           | Command                                                                                                        |
|----------------|----------------------------------------------------------------------------------------------------------------|
| SAD-R1 (C5)    | `lowatt-enedis cmdServicesAccesDonnees 25855571545617 --type ENERGIE --nom DUPONT`                             |
| SAD-R1 (C2-C4) | `lowatt-enedis cmdServicesAccesDonnees 98800003605600 --type ENERGIE --nom DUPONT`                             |
| SAD-R2 (C5)    | `lowatt-enedis cmdServicesAccesDonnees 24377424002398 --type CDC --period monthly --nom DUPONT`               |
| SAD-R2 (C2-C4) | `lowatt-enedis cmdServicesAccesDonnees 98800003605600 --type CDC --period monthly --nom DUPONT`               |
| SAD-R3 (C5)    | `lowatt-enedis cmdServicesAccesDonnees 24380318190106 --type IDX --period daily --nom DUPONT`               |
| SAD-R3 (C2-C4) | `lowatt-enedis cmdServicesAccesDonnees 98800003605600 --type IDX --period daily --nom DUPONT`               |
| SAD-R4 (C5)    | `lowatt-enedis cmdServicesAccesDonnees 25852098337945 --type IDX --type CDC --period daily --nom DUPONT`    |
| SAD-R4 (C2-C4) | `lowatt-enedis cmdServicesAccesDonnees 98800003605600 --type IDX --type CDC --period daily --nom DUPONT`    |
| SAD-NR1 (C5)   | `lowatt-enedis cmdServicesAccesDonnees 25855571545617 --type ENERGIE --nom DUPONT --no-autorisation`           |
| SAD-NR1 (C2-C4 | `lowatt-enedis cmdServicesAccesDonnees 98800003605600 --type ENERGIE --nom DUPONT --no-autorisation`           |
| SAD-NR2 (C5)   | `lowatt-enedis cmdServicesAccesDonnees 25855571545617 --type ENERGIE --nom DUPONT --to 2050-04-07`             |
| SAD-NR2 (C2-C4)| `lowatt-enedis cmdServicesAccesDonnees 98800003605600 --type ENERGIE --nom DUPONT --to 2050-04-07`             |

CommandeHistoriqueDonneesMesuresFines v1.0
------------------------------------------

| Case                   | Command                                                                                                                           |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| MFI-GK-R1 (C5)         | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 ENERGIE`                   |
| MFI-GK-R1 (C2-C4)      | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 ENERGIE`                   |
| MFI-GK-R2 (C5)         | `lowatt-enedis cmdHistoFine 25150217034354 COURBES`                                                                               |
| MFI-GK-R2 (C2-C4)      | `lowatt-enedis cmdHistoFine 98800004935121 COURBES`                                                                               |
| MFI-GK-R3 (C5)         | `lowatt-enedis cmdHistoFine 25150217034354 PMAX`                                                                                  |
| MFI-GK-R4 (C5)         | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 INDEX`                     |
| MFI-GK-R4 (C2-C4)      | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 INDEX`                     |
| MFI-GK-NR1 (C5)        | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 COURBES --from 2020-01-01` |
| MFI-GK-NR1 (C2-C4)     | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 COURBES --from 2020-01-01` |
| MFI-GK-NR2 (C5)        | `lowatt-enedis cmdHistoFine 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 INDEX --from 2020-01-01`   |
| MFI-GK-NR2 (C2-C4)     | `lowatt-enedis cmdHistoFine 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186 INDEX --from 2020-01-01`   |


CommandeHistoriqueDonneesMesuresFacturantes v1.0
------------------------------------------------

| Case                   | Command                                                                                                                                   |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| MFA-GK-R1 (C5)         | `lowatt-enedis cmdHistoFact 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289`                                   |
| MFA-GK-R1 (C2-C4)      | `lowatt-enedis cmdHistoFact 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186`                                   |
| MFA-GK-NR1 (C5)        | `lowatt-enedis cmdHistoFact 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289 --from 2025-10-01 --to 2025-08-01` |
| MFA-GK-NR1 (C2-C4)     | `lowatt-enedis cmdHistoFact 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186  --from 2025-10-01 --to 2025-08-01`|

CommandeInformationsTechniquesEtContractuelles v1.0
---------------------------------------------------

| Case                   | Command                                                                                                 |
|------------------------|---------------------------------------------------------------------------------------------------------|
| ITC-GK-R1 (C5)         | `lowatt-enedis cmdTechnical 25150217034354,25825036170379,25999131613803,50086054270348,25262662681289` |
| ITC-GK-R1 (C2-C4)      | `lowatt-enedis cmdTechnical 98800004935121,98800001544168,98800004938924,98800006694381,98800001220186` |

CommandeArretServiceSouscritMesures v1.0
----------------------------------------

| Case                   | Command                                                  |
|------------------------|----------------------------------------------------------|
| ASS-R1 (C5)            | `lowatt-enedis unsubscribe 25884515170669 --id 47761068` |
| ASS-R1 (C2-C4)         | `lowatt-enedis unsubscribe 98800000000246 --id 47761068` |

CommandeTransmissionDonneesInfraJ v1.0
--------------------------------------

| Case         | Command                                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------------------|
| F375A-R1     | `lowatt-enedis cmdInfraJ 98800000000246 --cdc --soutirage --denomination "Raison Sociale"`                           |
| F375A-NR1    | `lowatt-enedis cmdInfraJ 98800000000246 --idx --injection --denomination "Raison Sociale" --no-autorisation`         |
