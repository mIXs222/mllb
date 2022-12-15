import os as os
from operator import add
import matplotlib.pyplot as plt
import numpy as np

#Order for statistics in array and csv form:
#[duration, qps, avg_latency, 99th, 99.9th, 99.99th]

#MAKE SURE TO UPDATE ROOT_DIR_NAME from "test_output" if using different root directory names
ROOT_DIR_NAME = "test_output"
PLOT_DIR_NAME = "generated_plots"

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

    return zip(read_vec, update_vec)

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
    
    return results

def save_single_plot(labels, results, file_name, title, metric):
    fig, ax = plt.subplots()
    x = np.arange(len(labels))  # the label locations
    width = 0.5
    for i in range(len(labels)):
        rect = ax.bar(i, results[i], width, label=labels[i])

    ax.set_ylabel(metric)
    ax.set_title(title)
    ax.set_xticks(x, labels)
    ax.set_xlabel('Load Balancers')
    plt.savefig(file_name, colormap=plt.cm.gray)
    return True

def save_dict_plot(labels, resultDict, file_name, title, metric):
    fig, ax = plt.subplots()
    x = np.arange(len(labels))  # the label locations
    width = 0.5
    for i in range(len(labels)):
        rect = ax.bar(i, resultDict[labels[i]], width, label=labels[i])

    ax.set_ylabel(metric)
    ax.set_title(title)
    ax.set_xticks(x, labels)
    ax.set_xlabel('Load Balancers')
    plt.savefig(file_name)
    plt.close()
    return True

def results_to_plots(label, res):
    save_path = "./" + PLOT_DIR_NAME + "/" + label + "/"

    print("Generating plot for: " + label)
    print("--outputting to dir: " + save_path)

    labels = []
    read_thpt = []
    upd_thpt = []
    upd_lat = []
    read_lat = []
    thpt = []
    lat = []
    lat_99 = []
    lat_999 = []
    lat_9999 = []

    thptDict = {}
    latDict = {}
    lat99Dict = {}
    lat999Dict = {}

    for ele in res:
        print(ele[0])
        labels.append(ele[0])
        upd_thpt.append(ele[1][1][0])
        upd_lat.append(ele[1][1][1]/1000)
        read_thpt.append(ele[1][0][0])
        read_lat.append(ele[1][0][1]/1000)
        thpt.append(ele[1][2][0])
        lat.append(ele[1][2][1]/1000)

        thptDict[ele[0]] = ele[1][2][0]
        latDict[ele[0]] = ele[1][2][1]/1000
        lat99Dict[ele[0]] = ele[1][2][2]/1000
        lat999Dict[ele[0]] = ele[1][2][3]/1000

        lat_99.append(ele[1][2][2]/1000)
        lat_999.append(ele[1][2][3]/1000)
        lat_9999.append(ele[1][2][4]/1000)

    if len(thpt) > 0:
        sorted_labs = labels
        sorted_labs.sort()
        metric = 'Throughput (OPS)'
        title = metric + ' ' +  str(' '.join(label.split('_')))
        file_path = save_path + label + '_thpt.png'
        #save_single_plot(labels, thpt, file_path, title, metric)
        save_dict_plot(sorted_labs, thptDict, file_path, title, metric)

    if len(lat) > 0:
        sorted_labs = labels
        sorted_labs.sort()
        metric = 'Latency (ms)'
        title = metric + ' ' +  str(' '.join(label.split('_')))
        file_path = save_path + label + '_lat.png'
        save_dict_plot(sorted_labs, latDict, file_path, title, metric)

    if len(lat_99) > 0:
        metric = '99th percentile Latency (ms)'
        sorted_labs = labels
        sorted_labs.sort()
        title = metric + ' ' +  str(' '.join(label.split('_')))
        file_path = save_path + label + '_99lat.png'
        save_dict_plot(sorted_labs, lat99Dict, file_path, title, metric)
    
    if len(lat_999) > 0:
        metric = '99.9th percentile Latency (ms)'
        sorted_labs = labels
        sorted_labs.sort()
        title = metric + ' ' +  str(' '.join(label.split('_')))
        file_path = save_path + label + '_99.9lat.png'
        save_dict_plot(sorted_labs, lat999Dict, file_path, title, metric)
        
    return True

dirMap = {}
for root, dirs, files in os.walk("."):
    for _dir in dirs:
        if (_dir[:len(ROOT_DIR_NAME)] == ROOT_DIR_NAME):
            print(_dir)
            dirMap[_dir] = process_directory(_dir)


three_res = {}
five_res = {}
SETTINGS = ["het", "weak_het", "normal", "memhet"]

#Init Map lists using SETTINGS
for setting in SETTINGS:
    five_res[setting] = []
    three_res[setting] = []


for model in dirMap:
    if len(dirMap[model]) == 0:
        continue
    readout = [sum(x) for x in dirMap[model][0]]
    updateout = [sum(x) for x in dirMap[model][1]]
    totalout = [sum(x) for x in zip(readout, updateout)]

    print("\n" + model)
    print("format: [QPS, Avg(lat), 99th(lat), 99.9th(lat), 99.99th(lat)]")
    print("read stats: " + str(readout[1:]))
    print("update stats: " + str(updateout[1:]))
    print("combined stats:" + str(totalout[1:]))

    toks = model.split("_")[2:]
    if (toks[0] == '5'):
        key = "normal"
        if (len(toks) > 2):
            key = '_'.join(toks[2:])
        five_res[key].append((toks[1], [readout[1:], updateout[1:], totalout[1:]])) #each res -> SETTINGS -> model_name, results from each model
    else:
        key = "normal"
        if (len(toks) > 1):
            key = '_'.join(toks[1:])
        three_res[key].append((toks[0], [readout[1:], updateout[1:], totalout[1:]]))

for key in three_res:
    results_to_plots(key, three_res[key])
for key in five_res:
    results_to_plots("5_node_" + key, five_res[key])