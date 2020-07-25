import json
import boto3
import time

cwl = boto3.client('logs')

def lambda_handler(event, context):
    #TODO: implement nextToken for log groups
    lscount = 0
    ls2delete = 0
    lgcount = 0
    lg2delete = 0
    timeNow = int(round(time.time() * 1000))
    cwlg = cwl.describe_log_groups()
    for lgn in cwlg['logGroups']:
        print(lgn['logGroupName'])
        nextToken = ''
        while True:
            if nextToken:
                cwls = cwl.describe_log_streams(logGroupName=lgn['logGroupName'], nextToken=nextToken)
            else:
                cwls = cwl.describe_log_streams(logGroupName=lgn['logGroupName'])
            
            for lsn in cwls['logStreams']:
                lscount = lscount + 1
                print(lsn['logStreamName'])
                if 'lastEventTimestamp' in lsn:
                    if int(lsn['lastEventTimestamp']) < timeNow - 2678400000:
                        # if last event is older than 31 days
                        print(lsn['logStreamName'] + " will be deleted.")
                        ls2delete = ls2delete + 1
                        cwl.delete_log_stream(logGroupName=lgn['logGroupName'], logStreamName=lsn['logStreamName'])

            if 'nextToken' in cwls:
                nextToken = cwls['nextToken']
            else:
                break
    
    cwlg = cwl.describe_log_groups()
    for lgn in cwlg['logGroups']:
        lgcount = lgcount + 1
        cwls = cwl.describe_log_streams(logGroupName=lgn['logGroupName'])
        #print(cwls['logStreams'][0])
        if cwls['logStreams']:
            print(lgn['logGroupName'] + " has log streams")
        else:
            print(lgn['logGroupName'] + " is empty and will be deleted")
            lg2delete = lg2delete + 1
            cwl.delete_log_group(logGroupName=lgn['logGroupName'])
        
        
    print("Number of log groups before cleanup: " + str(lgcount))
    print("Number of log groups deleted: " + str(lg2delete))            
    print("Number of log streams before cleanup: " + str(lscount))
    print("Number of log streams deleted: " + str(ls2delete))
