import os as os
from operator import add

#Order for statistics in array and csv form:
#[duration, qps, avg_latency, 99th, 99.9th, 99.99th]

#MAKE SURE TO UPDATE ROOT_DIR_NAME from "test_output" if using different root directory names
ROOT_DIR_NAME = "test_output"

global_results = []

def process_directory(d):
    curpath = "./"+d
    f_list = []
    for _, _, files in os.walk(curpath):
        for f in files:
            f_list.append(f)

    return flist_to_csv(d, f_list)

def process_stat_list(s):
    read_qps = 0
    read_lat = 0
    read_dur = 0
    read_99 = 0
    read_999 = 0
    read_9999 = 0

    upd_qps = 0
    upd_dur = 0
    upd_lat = 0
    upd_99 = 0
    upd_999 = 0
    upd_9999 = 0

    read_lines = []
    upd_lines = []

    for stat in s:
        for word in stat.split():
            if (word == 'READ'):
               read_lines.append(stat.split()[4:])
               break

            if (word == 'UPDATE'):
                upd_lines.append(stat.split()[4:])
                break

    read_trials = len(read_lines)
    upd_trials = len(upd_lines)

    for linestat in read_lines:
        for x in range(1, len(linestat), 2):
            category = linestat[x-1][:-1]
            measure = linestat[x][:-1]
            
            if (category == 'Takes(s)'):
                read_dur += float(measure)
            if (category == 'OPS'):
                read_qps += float(measure)
            if (category == 'Avg(us)'):
                read_lat += float(measure)
            if (category == '99th(us)'):
                read_99 += float(measure) 
            if (category == '99.9th(us)'):
                read_999 += float(measure) 
            if (category == '99.99th(us)'):
                read_9999 += float(measure)

    for linestat in upd_lines:
        for x in range(1, len(linestat), 2):
            category = linestat[x-1][:-1]
            measure = linestat[x][:-1]
            
            if (category == 'Takes(s)'):
                upd_dur += float(measure)
            if (category == 'OPS'):
                upd_qps += float(measure)
            if (category == 'Avg(us)'):
                upd_lat += float(measure)
            if (category == '99th(us)'):
                upd_99 += float(measure) 
            if (category == '99.9th(us)'):
                upd_999 += float(measure) 
            if (category == '99.99th(us)'):
                upd_9999 += float(measure)
    
    read_vec = [read_dur, read_qps/read_trials, read_lat/read_trials, read_99/read_trials, read_999/read_trials, read_9999/read_trials]
    update_vec = [upd_dur, upd_qps/upd_trials, upd_lat/upd_trials, upd_99/upd_trials, upd_999/upd_trials, upd_9999/upd_trials]
    return zip(update_vec, read_vec)

def flist_to_csv(d, f_list):
    results = []
    print_next = 0
    for f in f_list:
        stat_list = []
        with open("./"+d+"/"+f, 'r') as fp:
            for line in fp:
                if print_next > 0:
                    stat_list.append(line)
                for word in line.split():
                    if (word == 'Run'):
                        stat_list.append(line)
                        print_next=3
                print_next-=1

        output_tuple = process_stat_list(stat_list)
        results.append(output_tuple)
    
    global_results.append([d, results])
    return results

dirMap = {}
for root, dirs, files in os.walk("."):
    for _dir in dirs:
        if (_dir[:len(ROOT_DIR_NAME)] == ROOT_DIR_NAME):
            print(_dir)
            dirMap[_dir] = process_directory(_dir)

#Sum all update reads between each client list in the dirMap
for model in dirMap:
    if len(dirMap[model]) == 0:
        continue
    readout = [sum(x) for x in dirMap[model][0]]
    updateout = [sum(x) for x in dirMap[model][1]]
    print(model)
    print("format: [time, QPS, Avg(lat), 99th(lat), 99.9th(lat), 99.99th(lat)]")
    print("read stats: " + str(readout))
    print("update stats: " + str(updateout))
