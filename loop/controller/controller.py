import pandas as pd
import threading
from nanoid import generate
import os
from datetime import datetime
from utils.utils import convertTimeStringIntoSeconds, getTimeStamp, getDateObject, getTimeOnly , getOffSet , getWeekDay
from models.report_data import ReportDB
REPORT_OUTPUT_PATH= os.path.join('CSV', 'output')
STORE_STATUS = 'store_status.csv'
STORE_BUSINESS_HOUR = 'store_business_hour.csv'
STORE_TIMEZONE = 'store_timezone.csv'

#extrapolate some week days based on the data we have to handle remaining days
def getAugumentedDf(business_hour_df: pd.DataFrame):
    all_store_id = business_hour_df['store_id'].unique()
    augumented_df = pd.DataFrame(columns= business_hour_df.columns)
    cnt=0
    for store_id in all_store_id:
        cnt+=1
        store= business_hour_df.loc[business_hour_df['store_id'] == store_id].copy()
        not_found_day = []
        sum_time_start = 0
        sum_time_end = 0
        for day in range(7):
            tmp_store= store.loc[store['day'] == day]
            if(len(tmp_store)==0):
                not_found_day.append(day)
                continue
            start_time_local_mean = store.loc[store['day'] == day, 'start_time_local'].map(convertTimeStringIntoSeconds).mean()
            end_time_local_mean = store.loc[store['day'] == day, 'end_time_local'].map(convertTimeStringIntoSeconds).mean()
            sum_time_start += start_time_local_mean
            sum_time_end += end_time_local_mean
            augumented_df.loc[len(augumented_df)] = [store_id, day, start_time_local_mean, end_time_local_mean]
        
        for day in not_found_day:
            augumented_df.loc[len(augumented_df)] = [store_id, day, 0, 3600*24-1]
            
        if(cnt==2000):
            break
    augumented_df['store_id']= augumented_df['store_id'].astype('int64' )
    augumented_df['day']= augumented_df['day'].astype('int16')
    return augumented_df

#calculate the uptime and downtime of the store for the last week
def getWeekUptime(store_status, augumented_business_hour_df):
    week_uptime = pd.DataFrame(columns=['store_id', 'last_week_uptime', 'last_week_downtime'])
    store_ids = augumented_business_hour_df['store_id'].unique()
    business_hour_indexed = augumented_business_hour_df.set_index(['store_id','day'])
    todays_timestamp = datetime.now().timestamp()
    one_week_in_seconds = 7*24*3600
    for store_id in store_ids:
        sum_active = 0
        sum_inactive= 0
        for day in range(7):
            _from , to = business_hour_indexed.loc[(store_id, day), ['start_time_local', 'end_time_local']]
            req_store_status = store_status.loc[(store_status['store_id'] == store_id) & (store_status['week_day'] == day)]
            
            first , last = (None,None), (None,None)
            for (ind , row_status) in req_store_status.iterrows():    
                timestamp = getTimeStamp(row_status['timestamp_utc'])
                if(timestamp < todays_timestamp - one_week_in_seconds):
                    continue
                date_of_read, time_of_read = getDateObject(row_status['timestamp_utc'])
                time_in_seconds = getTimeOnly(time_of_read)
                if( time_in_seconds >= _from and time_in_seconds <= to):
                    if first is None:
                        first = time_in_seconds , row_status['status']
                    else:
                        first = max(first, (time_in_seconds , row_status['status']))
                    
                    if last is None:
                        last = time_in_seconds , row_status['status']
                    else :
                        last = min(last , (time_in_seconds , row_status['status']))

                    if row_status['status'] == 'active':
                        sum_active += 3600
                    else :
                        sum_inactive += 3600
            
            if first[0] == None or last[0] == None:
                sum_active+= to-_from
                continue

            if first[0] < to:
                if first[1] == 'active':
                    sum_active += to-first[0]
                else: 
                    sum_inactive += to- first[0]
            
            if last[0] > _from :
                if last[1] == 'active':
                    sum_active += last[0] - _from 
                else: 
                    sum_inactive += last[0]- _from
            
        week_uptime.loc[len(week_uptime)] = [int(store_id), int(sum_active) , int(sum_inactive)]

    return week_uptime

#calculate the uptime and downtime of the store for the last day
def getDayUptime(store_status, augumented_business_hour_df):
    day_uptime = pd.DataFrame(columns=['store_id', 'last_day_uptime', 'last_day_downtime'])
    store_ids = augumented_business_hour_df['store_id'].unique()
    business_hour_indexed = augumented_business_hour_df.set_index(['store_id','day'])
    todays_timestamp = datetime.now().timestamp()
    todays_day_of_week = datetime.now().weekday()
    yesterdays_day_of_week = todays_day_of_week-1 if todays_day_of_week>0 else 6
    one_day_in_seconds = 24*3600
    for store_id in store_ids:
        sum_active = 0
        sum_inactive= 0
        day = yesterdays_day_of_week

        _from , to = business_hour_indexed.loc[(store_id, day), ['start_time_local', 'end_time_local']]
        req_store_status = store_status.loc[(store_status['store_id'] == store_id) & (store_status['week_day'] == day)]
        first , last = (None,None), (None,None)
        for (ind , row_status) in req_store_status.iterrows():    
            timestamp = getTimeStamp(row_status['timestamp_utc'])
            if(timestamp < todays_timestamp - one_day_in_seconds):
                continue
            date_of_read, time_of_read = getDateObject(row_status['timestamp_utc'])
            time_in_seconds = getTimeOnly(time_of_read)
            if( time_in_seconds >= _from and time_in_seconds <= to):
                if first is None:
                    first = time_in_seconds , row_status['status']
                else:
                    first = max(first, (time_in_seconds , row_status['status']))
                
                if last is None:
                    last = time_in_seconds , row_status['status']
                else :
                    last = min(last , (time_in_seconds , row_status['status']))

                if row_status['status'] == 'active':
                    sum_active += 3600
                else :
                    sum_inactive += 3600
        
        if first[0] == None or last[0] == None:
            sum_active+= to-_from
        else:
            if first[0] < to:
                if first[1] == 'active':
                    sum_active += to-first[0]
                else: 
                    sum_inactive += to- first[0]
            
            if last[0] > _from :
                if last[1] == 'active':
                    sum_active += last[0] - _from 
                else: 
                    sum_inactive += last[0]- _from
            
        day_uptime.loc[len(day_uptime)] = [int(store_id), int(sum_active) , int(sum_inactive)]

    return day_uptime

#calculate the uptime and downtime of the store for the last hour
def getHourUptime(store_status, augumented_business_hour_df):
    hour_uptime = pd.DataFrame(columns=['store_id', 'last_hour_uptime', 'last_hour_downtime'])
    store_ids = augumented_business_hour_df['store_id'].unique()
    business_hour_indexed = augumented_business_hour_df.set_index(['store_id','day'])
    todays_timestamp = datetime.now().timestamp()
    todays_day_of_week = datetime.now().weekday()
    yesterdays_day_of_week = todays_day_of_week-1 if todays_day_of_week>0 else 6
    for store_id in store_ids:
        sum_active = 0
        sum_inactive= 0
        day = yesterdays_day_of_week

        _from , to = business_hour_indexed.loc[(store_id, day), ['start_time_local', 'end_time_local']]
        req_store_status = store_status.loc[(store_status['store_id'] == store_id) & (store_status['week_day'] == day)]
        first , last = (None,None), (None,None)
        for (ind , row_status) in req_store_status.iterrows():    
            timestamp = getTimeStamp(row_status['timestamp_utc'])
            if(timestamp < todays_timestamp - 3600):
                continue
            date_of_read, time_of_read = getDateObject(row_status['timestamp_utc'])
            time_in_seconds = getTimeOnly(time_of_read)
            if( time_in_seconds >= _from and time_in_seconds <= to):
                if first is None:
                    first = time_in_seconds , row_status['status']
                else:
                    first = max(first, (time_in_seconds , row_status['status']))
                
                if last is None:
                    last = time_in_seconds , row_status['status']
                else :
                    last = min(last , (time_in_seconds , row_status['status']))

                if row_status['status'] == 'active':
                    sum_active += 3600
                else :
                    sum_inactive += 3600
        
        if first[0] == None or last[0] == None:
            sum_active+= to-_from
        else:
            if first[0] < to:
                if first[1] == 'active':
                    sum_active += to-first[0]
                else: 
                    sum_inactive += to- first[0]
            
            if last[0] > _from :
                if last[1] == 'active':
                    sum_active += last[0] - _from 
                else: 
                    sum_inactive += last[0]- _from
            
        hour_uptime.loc[len(hour_uptime)] = [int(store_id), int(sum_active) , int(sum_inactive)]

    return hour_uptime


#generate report in a thread and save it as a file and update the status of the report to finished
def generateReportThread(report_id):
    business_hour_df= pd.read_csv("./CSV/store_business_hour.csv")
    store_status = pd.read_csv('./CSV/store_status.csv')
    store_timezone = pd.read_csv('./CSV/store_timezone.csv').set_index('store_id')
    store_timezone['offset'] = store_timezone['timezone_str'].map(getOffSet)
    store_timezone.drop('timezone_str', axis=1, inplace=True)
    augumented_business_hour_df= getAugumentedDf(business_hour_df)
    store_status['week_day'] = store_status['timestamp_utc'].map(getWeekDay)
    store_status['timestamp_seconds'] = store_status['timestamp_utc'].map(getTimeStamp)
    def addOffset(time,store_id):
        try:
            return time - store_timezone.loc[store_id, 'offset']
        except:
            return time- getOffSet('America/Chicago')
        
    for (ind,row) in augumented_business_hour_df.iterrows():
        store_id = row['store_id']
        store_id = int(store_id)
        row['start_time_local']= addOffset(row['start_time_local'], store_id)
        row['end_time_local']= addOffset(row['end_time_local'], store_id)
        augumented_business_hour_df.loc[ind] = row
        break

    week_uptime = getWeekUptime(store_status, augumented_business_hour_df)
    day_uptime = getDayUptime(store_status , augumented_business_hour_df)
    hour_uptime = getHourUptime(store_status , augumented_business_hour_df)
    result = pd.merge(left= day_uptime , right= week_uptime)
    result = pd.merge(left = hour_uptime , right = result)
    report_path = f'{REPORT_OUTPUT_PATH}/report_{report_id}.csv'
    result.to_csv(report_path , index=False)
    ReportDB.update_report_status_to_finished(report_id)
    ReportDB.getStatusOf(report_id)
    return week_uptime
    
#main controller for trigger report generation
def generateReport():
    report_id=generate()
    ReportDB.insert_report(report_id)
    th= threading.Thread(target=generateReportThread, args = (report_id,) )
    th.start()
    return report_id



