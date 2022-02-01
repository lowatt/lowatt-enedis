#!/bin/sh
set -ex

# based on Enedis.SGE.REF.0465.Homologation_Catalogue des cas de tests_Tiers_SGE22.1_v1.0.pdf

# Export these environment variables or the script will fail
# export ENEDIS_KEY_FILE=XXX
# export ENEDIS_CERT_FILE=XXX
# export ENEDIS_LOGIN=XXX
# export ENEDIS_CONTRAT=XXX
export ENEDIS_HOMOLOGATION=on

echo "***************************** ConsultationDonneesTechniquesContractuelles v0"

echo "ADP-R1 - Accès aux données d’un point avec autorisation"
lowatt-enedis technical --autorisation 98800007059999
lowatt-enedis technical --autorisation 25946599093143

echo "ADP-R2 - Accès aux données d’un point sans autorisation"
lowatt-enedis technical 98800007059999
lowatt-enedis technical 25946599093143

echo "ADP-NR1 Accès aux données d’un point inexistant"
lowatt-enedis technical 99999999999999


echo "***************************** ConsultationMesures v1.1"

echo "AHC-R1 - Accès à l’historique de consommations avec autorisation"
lowatt-enedis measures --autorisation 98800005782026
lowatt-enedis measures --autorisation 25957452924301

echo "AHC-NR1 - Accès à l’historique de consommations sans autorisation"
lowatt-enedis measures 98800005782026


echo "***************************** ConsultationMesuresDetaillees v2.0"

echo "CMD2-R1 - Accès à l’historique de courbe de charge avec autorisation"
lowatt-enedis details 30001610071843 COURBE --from 2020-03-01 --to 2020-03-08
lowatt-enedis details 25478147557460 COURBE --from 2020-03-01 --to 2020-03-08

echo "CMD2-R2 - Accès à l’historique des courbes de puissance réactive avec autorisation"
lowatt-enedis details 30001610071843 COURBE --courbe-type PRI --from 2020-03-01 --to 2020-03-08

echo "CMD2-R3 - Accès à l’historique des énergies globales quotidiennes avec autorisation"
lowatt-enedis details 25478147557460 ENERGIE --from 2020-03-01 --to 2020-03-08

echo "CMD2-R4 - Accès à l’historique de puissances maximales quotidiennes ou mensuelles avec autorisation"
lowatt-enedis details 25478147557460 PMAX --from 2020-01-01 --to 2020-02-01

echo "CMD2-NR1 - Accès à l’historique de courbe de charge dont la profondeur maximale (7 jours) n'est pas respectée"
lowatt-enedis details 25478147557460 COURBE --from 2020-01-01 --to 2020-01-10

echo "CMD2-NR2 - Accès à l’historique des énergies globales quotidiennes sans autorisation"
# XXX: implement -(-no)-autorisation for details
#lowatt-enedis details 25478147557460 ENERGIE --from 2020-01-01 --to 2020-01-08


echo "***************************** RecherchePoint v2.0"

echo "RP-R1 - Recherche à partir de critères autres que les données du client"
lowatt-enedis search --tension BTINF --categorie RES --cp 34650 --insee 34231

echo "RP-R2 - Recherche du N° de PRM à partir de l’adresse et du nom exact du client pour un fournisseur non titulaire du point"
lowatt-enedis search --voie "1 RUE DE LA MER" --nom=TEST --cp 84160 --insee 84042 --hp

echo "RP-R3 - Recherche d’un point avec adresse exacte et nom approchant (chaîne de plus de trois caractères incluse dans le nom/dénomination sociale)"
lowatt-enedis search --voie "1 RUE DE LA MER" --nom=TES --cp 84160 --insee 84042 --hp

echo "RP-NR1 - Recherche avec des critères retournant plus de 200 points"
lowatt-enedis search --categorie RES --cp 34650 --insee 34231

echo "RP-NR2 - Recherche avec des critères insuffisants"
lowatt-enedis search --insee 34231 --voie "1 RUE DE LA MER"


echo "***************************** CommandeCollectePublicationMesures"


echo "***************************** RechercheServicesSouscritsMesures"


echo "***************************** CommandeArretServiceSouscritMesures"


echo "***************************** CommandeTransmissionDonneesInfraJ v1.0"

echo "F375A-R1 - Demande de transmission de données infra-journalières avec autorisation"
# FAIL lowatt-enedis cmdInfraJ 98800000000246 --cdc --injection --denomination "Raison Sociale"

echo "F375A-NR1 - Demande de transmission de données infra-journalières sans autorisation"
echo "XXX commente autorisation dans code"
# lowatt-enedis cmdInfraJ 98800000000246 --idx --injection --denomination "Raison Sociale"


echo "***************************** CommandeTransmissionHistoriqueMesures v1.0"

echo "F380-R1 - Demande de transmission d’historique de courbe de charge avec autorisation"
lowatt-enedis cmdHisto 25957452924301 CDC --pas 30 --nom roro --civilite M
lowatt-enedis cmdHisto 98800005144497 CDC --pas 10

echo "F385B-R1 - Demande de transmission d’historique d’index quotidiens avec autorisation"
lowatt-enedis cmdHisto 25957452924301 IDX --nom roro --civilite M

echo "F380-NR1 - Demande de transmission d’historique de courbe de charge dont la profondeur maximale de 24 mois n’est pas respectée"
lowatt-enedis cmdHisto 25957452924301 CDC --pas 30 --nom roro --civilite M --from 2010-01-01

echo "F385B-NR1 - Demande de transmission d’historique d’index quotidiens d’un point avec une date de début à plus de 36 mois"
lowatt-enedis cmdHisto 25957452924301 IDX --nom roro --civilite M --from 2010-01-01
