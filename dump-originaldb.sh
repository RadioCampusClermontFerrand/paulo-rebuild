#!/bin/sh

# remarque: ce script doit être lancé sur le système encore fonctionnel. Si on récupère uniquement la partition racine, 
# il suffit de s'y rendre, puis d'utiliser la commande chroot pour simuler l'ancien système, le temps de récupérer 
# la base de données
echo "Démarrage de MySQL"
/etc/init.d/mysql start

sleep 5
echo "Mise à jour de la base"
SQL="SELECT t_bande.ban_nom, tit_file, tit_nom, alb_nom, t_groupe.grp_nom, mus_nom, t_langue.lan_nom, t_rotation.rot_nom, t_titre.tit_code
    INTO OUTFILE '/tmp/backup-titres.csv' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' LINES TERMINATED BY '\n' 
    FROM 
        t_titre
    LEFT JOIN t_musical ON t_titre.tit_code=t_musical.tit_code
    LEFT JOIN t_bande ON t_titre.ban_code=t_bande.ban_code
    LEFT JOIN t_type_musical ON t_musical.mus_code=t_type_musical.mus_code
    LEFT JOIN t_album ON t_album.alb_code = t_titre.alb_code
    LEFT JOIN t_groupe ON t_groupe.grp_code=t_titre.grp_code
    LEFT JOIN t_langue ON t_langue.lan_code=t_titre.lan_code
    LEFT JOIN t_rotation ON t_rotation.rot_code=t_titre.rot_code"

mysql paulo3 -e "$SQL;"

echo "Arrêt de MySQL"
/etc/init.d/mysql stop
