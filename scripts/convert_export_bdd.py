#!/usr/bin/python
# -*- coding: utf-8 -*-
#recupere les liens des trois reseaux pour exporter les reseaux au format texte
import sys
import math

import parameters
import subprocess
path_req= parameters.path_req
#print parameters.name_data_real
name_bdd =  parameters.name_bdd
dump_cmd = "sqlite3 "+name_bdd+" .dump > "+name_bdd + '.sql'
print dump_cmd
subprocess.call(dump_cmd,shell=True)
cat_cmd = "cat " + name_bdd + '.sql' + " | sed -e '" + 's/"//' + "g' > " + path_req +  "MysqlDump.sql.temp" 
print cat_cmd
subprocess.call(cat_cmd,shell=True)
mov_cmd = "mv " + path_req +  "MysqlDump.sql.temp "  +  name_bdd + '.sql'
print mov_cmd
subprocess.call(mov_cmd,shell=True)
tar_cmd = "gzip  "+name_bdd + '.sql'+ '.gz ' +  name_bdd + '.sql'
print tar_cmd
subprocess.call(tar_cmd,shell=True)
#tar -czvf sauvegarde.gz sauvegarde.sql


#scp -p cointet@polux.iscpif.fr:Bureau/indexing-tools-v2.7/sorties/export_MESR_20100722.lflsociete174/sauvegarde.gz .
server = parameters.server
reduced = name_bdd.split('/')[-1]
scp_cmd = "scp -p " +  name_bdd + '.sql'+ '.gz '  + server + ':/var/lib/mysql/' + reduced + '.sql'+'.gz'
print scp_cmd
subprocess.call(scp_cmd,shell=True)

# ssh_con = "ssh " + parameters.server
# subprocess.call(ssh_con,shell=True)
# 
# cd_cmd = 'cd /var/lib/mysql'
# subprocess.call(cd_cmd,shell=True)
# 
# 
# bdd_con = "mysql -u root -p"
# subprocess.call(bdd_con,shell=True)



# gunzip sauvegarde.gz
# mysql -u root -p
# > use veille;
# > create database veille;
# > source sauvegarde.sql;
# 
# mysql -u cointet -p  veille <concepts.sql
