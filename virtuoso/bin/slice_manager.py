import operator
import sqlite3
import time
import pdb

start_time = time.time()

# Check if DB exists and Delete it
if sqlite3.connect('manage.db'):
    conn = sqlite3.connect('manage.db')
    curs = conn.cursor()
    curs.execute('drop table if exists manage')
    conn.close()

# Create DB for latency mapping to link
conn = sqlite3.connect('manage.db')
curs = conn.cursor()
curs.execute('create table manage (switches, link, latency)')
###### STATIC CODE ##########
values = [('s1s2', 1, 1.0), ('s1s2', 2, 2.0), ('s1s2', 3, 1.0), ('s1s2', 4, 5.0),
          ('s2s3', 1, 2.0), ('s2s3', 2, 3.0), ('s2s3', 3, 1.0), ('s2s3', 4, 5.0),
          ('s3s4', 1, 3.0), ('s3s4', 2, 1.0), ('s3s4', 3, 3.0), ('s3s4', 4, 1.0),
          ('s4s0', 1, 4.0), ('s4s0', 2, 5.0), ('s4s0', 3, 6.0), ('s4s0', 4, 2.0)]
curs.executemany('insert into manage values(?,?,?)', values)
conn.commit()
conn.close()

# DB to dict(): format ex) [{'switch1': [['link1','latency1'], ['link2','latency2']] }]
conn = sqlite3.connect('manage.db')
curs = conn.cursor()
curs.execute('select * from manage')
rows = list(curs.fetchall())
manage =list()
###### STATIC CODE ##########
switches_name = ['s1s2', 's2s3', 's3s4', 's4s0']
for name in switches_name:
    tmp=list()
    for i in rows:
        if i[0] == name:
            tmp.append([i[1], i[2]])
        else:
            continue
    spf=dict()
    spf[name] = tmp
    manage.append(spf)

# Sorting the lowest latency in SPF: format ex) [{'switch1': [('link1','latency1'), ('link2','latency2')] }]
for spf in manage:
    values = spf[spf.keys()[0]]
    tmp=list()
    for v in values: tmp.append(tuple(v));
    spf[spf.keys()[0]] = sorted(tmp, key=lambda x: x[1])
print "[LOG] Initial latencies of SPF: ", manage

def change_maximum_spf(max_spf):
    # Find the maximum SPF
    for spf in manage:
        if spf.keys()[0] == max_spf.keys()[0]:
            # IF this SPF latency was chaged from {'s4s0': (4, 2.0)} to {'s4s0': (4, 1.0)}
            # TODO: Should to bring new calcurated latencies map
            ###### STATIC CODE ##########
            spf[spf.keys()[0]] = [(4, 1.0), (1, 4.0), (2, 5.0), (3, 6.0)]
            print "[LOG] Max latency SPF Changed: ", spf
        else:
            continue
    return manage        

def check_to_meet_sla(sla_latency=0.0, all_latency=0.0, all_path=list()):
    if all_latency > sla_latency:
        max_latency_spf = 0.0
        max_spf={}
        for path in all_path:
            # Find maximum latency of SPF in a entire path
            if max_latency_spf < path[path.keys()[0]][1]:
                max_latency_spf = path[path.keys()[0]][1]
                max_spf = path
            else:
                continue
        print "[LOG] sla_latency: ", sla_latency, "init_all_latency: ", all_latency, "all_path: ", all_path
        return change_maximum_spf(max_spf=max_spf)
        
# Finding Minimum latency Path
all_latency = 0.0
###### STATIC CODE ##########
sla_latency=4.0
all_path = []
for spf in manage:
    for link in spf[spf.keys()[0]]:
        all_latency += link[1]
        path = {spf.keys()[0]: link}
        all_path.append(path)
        # Check to meet SLA latency (GIVEN STATIC LATENCY)
        new_manage = check_to_meet_sla(sla_latency=sla_latency, all_latency=all_latency, all_path=all_path)
        break

all_latency = 0.0
# Applying the all path to service
for spf in new_manage:
    for link in spf[spf.keys()[0]]:
        all_latency += link[1]
        path = {spf.keys()[0]: link}
        all_path.append(path)
        break

print "[FINAL] sla_latency: ", sla_latency, "init_all_latency: ", all_latency, "all_path: ", all_path    

total_time = time.time() - start_time
print "TOTAL TIME: ", total_time

## END
