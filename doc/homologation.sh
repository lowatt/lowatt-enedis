#!/bin/sh

if test -z "$HOMOLOGATION_USER"; then
  echo "please provide HOMOLOGATION_USER environment variable"
  exit 1
fi

if test -z "$HOMOLOGATION_CONTRAT"; then
  echo "please provide HOMOLOGATION_CONTRAT environment variable"
  exit 1
fi

echo "***************************** ConsultationDonneesTechniquesContractuelles"

echo "ADP-R1 - Accès aux données d’un point avec autorisation"
lowatt-enedis technical --homologation $HOMOLOGATION_USER --autorisation 98800007059999
lowatt-enedis technical --homologation $HOMOLOGATION_USER --autorisation 09700274864887
lowatt-enedis technical --homologation $HOMOLOGATION_USER --autorisation 25946599093143

echo "ADP-R2 - Accès aux données d’un point sans autorisation"
lowatt-enedis technical --homologation $HOMOLOGATION_USER 98800007059999
lowatt-enedis technical --homologation $HOMOLOGATION_USER 09700274864887
lowatt-enedis technical --homologation $HOMOLOGATION_USER 25946599093143

echo "ADP-NR1 Accès aux données d’un point inexistant"
lowatt-enedis technical --homologation $HOMOLOGATION_USER 99999999999999


echo "***************************** ConsultationMesures"

echo "AHC-R1 - Accès à l’historique de consommations avec autorisation"
lowatt-enedis measures --homologation $HOMOLOGATION_USER --autorisation 98800007059999 $HOMOLOGATION_CONTRAT
# FAIL lowatt-enedis measures --homologation $HOMOLOGATION_USER --autorisation 09793183698380 $HOMOLOGATION_CONTRAT
lowatt-enedis measures --homologation $HOMOLOGATION_USER --autorisation 25110853825340 $HOMOLOGATION_CONTRAT

echo "AHC-NR1 - Accès à l’historique de consommations sans autorisation"
lowatt-enedis measures --homologation $HOMOLOGATION_USER 98800007059999 $HOMOLOGATION_CONTRAT


echo "***************************** ConsultationMesuresDetaillees"

echo "CMD-R1 - Accès à l’historique de courbe de charge avec autorisation"
lowatt-enedis details --homologation $HOMOLOGATION_USER 30001610071843 COURBE --from 2020-03-01 --to 2020-03-08
lowatt-enedis details --homologation $HOMOLOGATION_USER 25478147557460 COURBE --from 2020-03-01 --to 2020-03-08

echo "CMD-R2 - Accès à l’historique des courbes de puissance réactive avec autorisation"
lowatt-enedis details --homologation $HOMOLOGATION_USER 30001610071843 COURBE --courbe-type PRI --from 2020-03-01 --to 2020-03-08

echo "CMD-R3 - Accès à l’historique des énergies globales quotidiennes avec autorisation"
lowatt-enedis details --homologation $HOMOLOGATION_USER 25478147557460 ENERGIE --from 2020-03-01 --to 2020-03-08

echo "CMD-R4 - Accès à l’historique de puissances maximales quotidiennes ou mensuelles avec autorisation"
lowatt-enedis details --homologation $HOMOLOGATION_USER 25478147557460 PMAX --from 2020-01-01 --to 2020-02-01

echo "CMD-NR1 - Accès à l’historique de courbe de charge dont la profondeur maximale (7 jours) n'est pas respectée"
lowatt-enedis details --homologation $HOMOLOGATION_USER 25478147557460 COURBE --from 2020-01-01 --to 2020-01-10

echo "CMD-NR2 - Accès à l’historique des énergies globales quotidiennes sans autorisation"
#lowatt-enedis details --homologation $HOMOLOGATION_USER 25478147557460 ENERGIE --from 2020-01-01 --to 2020-01-08


echo "***************************** RecherchePoint"

echo "RP-R1 - Recherche à partir de critères autres que les données du client"
lowatt-enedis search --homologation $HOMOLOGATION_USER --tension HTA --categorie PRO --cp 40280 --insee 40281

echo "RP-R2 - Recherche du N° de PRM à partir de l’adresse et du nom exact du client pour un fournisseur non titulaire du point"
lowatt-enedis search --homologation $HOMOLOGATION_USER --voie "404 RUE DES CIMBRES" --nom=Homologation --cp 83380 --insee 83107 --hp

echo "RP-NR1 - Recherche avec des critères retournant plus de 200 points"
lowatt-enedis search --homologation $HOMOLOGATION_USER --categorie PRO --cp 40280 --insee 40281

echo "RP-NR2 - Recherche avec des critères insuffisants"
lowatt-enedis search --homologation $HOMOLOGATION_USER --categorie PRO --insee 40281


echo "***************************** CommandeCollectePublicationMesures"


echo "***************************** RechercheServicesSouscritsMesures"


echo "***************************** CommandeArretServiceSouscritMesures"


echo "***************************** CommandeTransmissionDonneesInfraJ"

echo "F375A-R1 - Demande de transmission de données infra-journalières avec autorisation"
# FAIL lowatt-enedis cmdInfraJ --homologation $HOMOLOGATION_USER 98800000000246 $HOMOLOGATION_CONTRAT  --cdc --injection --denomination "Raison Sociale"

echo "F375A-NR1 - Demande de transmission de données infra-journalières sans autorisation"
echo "XXX commente autorisation dans code"
# lowatt-enedis cmdInfraJ --homologation $HOMOLOGATION_USER 98800000000246 $HOMOLOGATION_CONTRAT --idx --injection --denomination "Raison Sociale"


echo "***************************** CommandeTransmissionHistoriqueMesures"

echo "F380-R1 - Demande de transmission d’historique de courbe de charge avec autorisation"
lowatt-enedis cmdHisto --homologation $HOMOLOGATION_USER 98800005144497 $HOMOLOGATION_CONTRAT CDC --pas 10
lowatt-enedis cmdHisto --homologation $HOMOLOGATION_USER 25110853825340 $HOMOLOGATION_CONTRAT CDC --pas 30 --nom roro --civilite M

echo "F385B-R1 - Demande de transmission d’historique d’index quotidiens avec autorisation"
lowatt-enedis cmdHisto --homologation $HOMOLOGATION_USER 25110853825340 $HOMOLOGATION_CONTRAT IDX --nom roro --civilite M

echo "F380-NR1 - Demande de transmission d’historique de courbe de charge dont la profondeur maximale de 24 mois n’est pas respectée"
lowatt-enedis cmdHisto --homologation $HOMOLOGATION_USER 25110853825340 $HOMOLOGATION_CONTRAT CDC --pas 30 --nom roro --civilite M --from 2010-01-01

echo "F385B-NR1 - Demande de transmission d’historique d’index quotidiens d’un point avec une date de début à plus de 36 mois"
lowatt-enedis cmdHisto --homologation $HOMOLOGATION_USER 25110853825340 $HOMOLOGATION_CONTRAT IDX --nom roro --civilite M --from 2010-01-01
