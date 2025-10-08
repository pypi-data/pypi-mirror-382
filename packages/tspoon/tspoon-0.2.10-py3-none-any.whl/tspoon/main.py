########################################################################################
#
# Utility fuctions - Date, Text, Time-series, Plotting
# Created by Beomseok Seo 2023.01.01
# Modified by Beomseok Seo 2024.01.01
#
########################################################################################

import os, time, sys
import pickle
import pandas as pd
import numpy as np
import regex as re
import datetime as dt
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt
import statsmodels.api as sm
import copy

from statsmodels.tsa.filters.hp_filter import hpfilter
from statsmodels.tsa.x13 import x13_arima_analysis
from statsmodels.tsa.ar_model import AutoReg

#date functions

def firstdate(Y,m):
    return dt.date(int(Y),int(m),1).strftime('%Y-%m-%d')

def lastdate(Y,m):
    return (dt.date(int(Y),int(m),1)+relativedelta(months=1)-dt.timedelta(days=1)).strftime('%Y-%m-%d')

def datesbetween(startdate, enddate):
    start_dt = dt.datetime.strptime(startdate,'%Y-%m-%d')
    end_dt = dt.datetime.strptime(enddate,'%Y-%m-%d')
    delta = dt.timedelta(days=1)

    dates = []

    while start_dt <= end_dt:
        dates.append(start_dt.strftime('%Y-%m-%d'))
        start_dt += delta

    return dates

def daytrans(basedate):
    return dt.date(int(basedate[:4]),int(basedate[4:6]),int(basedate[6:])).strftime('%Y-%m-%d')

def timetrans(basedate):
    return dt.time(int(basedate[:2]),int(basedate[2:4]),int(basedate[4:])).strftime('%H:%M:%S')

def dayahead(basedate,dayahead):
    if len(basedate) == 8:
        return (dt.date(int(basedate[:4]),int(basedate[4:6]),int(basedate[6:]))-dt.timedelta(dayahead)).strftime('%Y%m%d')
    elif len(basedate) == 10:
        return (dt.date(int(basedate[:4]),int(basedate[5:7]),int(basedate[8:]))-dt.timedelta(dayahead)).strftime('%Y-%m-%d')

def dateexp(basedate):
    return dt.date(int(basedate[:4]),int(basedate[5:7]),int(basedate[8:])).strftime('%Y.%m.%d')

def dayafter(basedate,dayahead):
    if len(basedate) == 8:
        return (dt.date(int(basedate[:4]),int(basedate[4:6]),int(basedate[6:]))+dt.timedelta(dayahead)).strftime('%Y%m%d')
    elif len(basedate) == 10:
        return (dt.date(int(basedate[:4]),int(basedate[5:7]),int(basedate[8:]))+dt.timedelta(dayahead)).strftime('%Y-%m-%d')

def day2week(basedate):
    if len(basedate) == 8:
        isodate = dt.date(int(basedate[0:4]), int(basedate[4:6]), int(basedate[6:8])).isocalendar()
    elif len(basedate) == 10:
        isodate = dt.date(int(basedate[0:4]), int(basedate[5:7]), int(basedate[8:10])).isocalendar()
    return(str(isodate[0]*100+isodate[1]))

def day2month(basedate):
    if len(basedate) == 8:
        md = str(basedate)[0:4]+str(basedate)[4:6]
    elif len(basedate) == 10:
        md = str(basedate)[0:4]+str(basedate)[5:7]
    return(md) 

def day2year(x):
    yd = str(x)[0:4]
    return(yd) 

def month2quarter(x):
    if str(x)[-2:] in ['01','02','03']:
        qq = 'q1'
    elif str(x)[-2:] in ['04','05','06']:
        qq = 'q2'
    elif str(x)[-2:] in ['07','08','09']:
        qq = 'q3'
    elif str(x)[-2:] in ['10','11','12']:
        qq = 'q4'
    mq = str(x)[:4]+qq
    return(mq)

def quarter2month(x):
    if str(x)[-2:] in ['q1','Q1']:
        mm = '03'
    elif str(x)[-2:] in ['q2','Q2']:
        mm = '06'
    elif str(x)[-2:] in ['q3','Q3']:
        mm = '09'
    elif str(x)[-2:] in ['q4','Q4']:
        mm = '12'
    mq = str(x)[:4]+mm
    return(mq)    

def week2day(x):
    if (sys.version.split(' ')[0])>='3.8':
        # wd = dt.date.fromisocalendar(int(str(x)[0:4]), int(str(x)[4:6]), 1)
        wd = dt.datetime.strptime(str(x)[0:4]+'-W'+str(x)[4:6]+'-'+str(1), "%Y-W%W-%w")
    else:
        wd = dt.datetime.strptime(str(x)[0:4]+'-W'+str(x)[4:6]+'-'+str(1), "%Y-W%W-%w")
    return(wd.strftime('%Y-%m-%d'))

def month2day(x, day='first', dformat='yyyy-mm-dd'):
    if len(x) > 6:
        x = str(x)[0:4]+str(x)[5:7]
    if day=='first':
        md = dt.date(int(str(x)[0:4]),int(str(x)[4:6]),1)
    elif day=='last':
        md = dt.date(int(str(x)[0:4]),int(str(x)[4:6])+1,1)-dt.timedelta(dayahead)
    if dformat=='yyyy-mm-dd':
        return(md.strftime('%Y-%m-%d'))
    elif dformat=='yyyymmdd':
        return(md.strftime('%Y%m%d'))


def backwardMovingAverage(TS, lag_day=14, dd=None, todf=False):
    if todf is True:
        val = [np.mean(TS[i-lag_day+1:i+1]) for i in range(lag_day,len(TS))]
        df = pd.DataFrame(val, index = TS.index[lag_day:])
        return(df, None)
    else:
        return([np.mean(TS[i-lag_day+1:i+1]) for i in range(lag_day,len(TS))], dd[lag_day:])
    
def bMA(TS, lag_day=14, dd=None, todf=False):
    if todf is True:
        val = [np.mean(TS[i-lag_day+1:i+1]) for i in range(lag_day,len(TS))]
        df = pd.DataFrame(val, index = TS.index[lag_day:])
        return(df)
    else:
        return([np.mean(TS[i-lag_day+1:i+1]) for i in range(lag_day,len(TS))])    
    
def cMA(TS, lag_day=14, lead_day=14, dd=None, todf=False):
    if todf is True:
        val = [np.mean(TS[i-lag_day+1:i+lead_day]) for i in range(lag_day,len(TS)-lead_day)]
        df = pd.DataFrame(val, index = TS.index[lag_day:len(TS)-lead_day])
        return(df)
    else:
        return([np.mean(TS[i-lag_day+1:i+1]) for i in range(lag_day,len(TS))])     
    

def cutTimeSeries(TS,DTS, START_DAY='2020-01-01'):
    dd_ = [dt.date(int(i[0:4]),int(i[5:7]),int(i[8:10])) for i in DTS]
    dd_ = [i>dt.date(int(START_DAY[0:4]),int(START_DAY[5:7]),int(START_DAY[8:10])) for i in dd_]    
    return(np.array(TS)[dd_],np.array(DTS)[dd_])



def yoy(dat, period=12, smooth=None):
    if smooth is not None:
        base = cMA(dat, lag_day=smooth[0], lead_day=smooth[1], todf=True).shift(period)
        return (dat/base*100-100).iloc[period:]
    else:
        return (dat/dat.shift(period)*100-100).iloc[period:]

def mom(dat, period=1):
    return (dat/dat.shift(period)*100-100).iloc[period:]
    
def unyoy(dat_yoy, dat_level, period=52, smooth=None, max_iter=3, backward=False, backward_beginning_index=None):
    if smooth is not None:
        base = cMA(dat_level, lag_day=smooth[0], lead_day=smooth[1], todf=True).squeeze()
    else:
        base = dat_level

    flag_f = dat_yoy.index == base.dropna().index[-1]
    if np.any(flag_f):
        base = pd.concat([base.loc[:base.dropna().index[-1]],pd.Series(np.nan, index=dat_yoy.index[np.where(flag_f)[0][0]+1:])])

    k = dat_yoy.dropna().index[-1]

    pred_level = ((dat_yoy+100)/100*base.shift(period))

    i=1
    while np.isnan(pred_level.loc[k]):
        flag = pred_level.index == base.dropna().index[-1]
        base = pd.concat([base.loc[:base.dropna().index[-1]], pred_level.iloc[np.where(flag)[0][0]+1:]])
        pred_level = ((dat_yoy+100)/100*base.shift(period))
        i+=1
        if i >max_iter:
            raise Exception("Something is wrong in the iteration of computing pred_level!")\

    pred_level[base.index[:period]] = base.iloc[:period]

    if backward:
        flag_b = dat_yoy.index == base.dropna().index[0]

        if np.any(flag_b):
            base = pd.concat([pd.Series(np.nan, index=dat_yoy.index[:np.where(flag_b)[0][0]]), base.loc[base.dropna().index[0]:]])

        k = dat_yoy.dropna().index[0]

        if backward_beginning_index is not None:
            pred_level = pd.concat([pd.Series(np.nan, index=backward_beginning_index), pred_level])
            dat_yoy = pd.concat([pd.Series(np.nan, index=backward_beginning_index), dat_yoy])
            base = pd.concat([pd.Series(np.nan, index=backward_beginning_index), base])
            flag_b = list([False for i in range(len(backward_beginning_index))]) + list(flag_b)

            if dat_yoy.dropna().index[0] == dat_yoy.index[0]:
                k = backward_beginning_index[0]
            else:
                k = dat_yoy.index[max(0,np.where(dat_yoy.index==dat_yoy.dropna().index[0])[0][0]-period)]

        pred_level_back = (base/((dat_yoy+100)/100)).shift(-period)

        i=1
        while np.isnan(pred_level_back.loc[k]):
            flag = pred_level_back.index == base.dropna().index[0]
            base = pd.concat([pred_level_back.iloc[:np.where(flag)[0][0]], base.loc[base.dropna().index[0]:]])
            pred_level_back = (base/((dat_yoy+100)/100)).shift(-period)
            i+=1
            if i >max_iter:
                raise Exception("Something is wrong in the iteration of computing pred_level!")       

        pred_level[dat_yoy.index[:np.where(flag_b)[0][0]]] = pred_level_back.loc[dat_yoy.index[:np.where(flag_b)[0][0]]]

    return pred_level

def naoutlier(df, quantile=0.99):
    q = df.quantile(quantile)
    return df[df < q]

# dataframe function    

def GenDf_d2w(df_d, aggregate='last'):
    df_dw = copy.deepcopy(df_d)
    df_dw.index = [day2week(x) for x in df_dw.index]
    df_dw.index.name = 'index'
    if aggregate=='last':
        df_w = df_dw[~df_dw.index.duplicated(keep='last')]   
    if aggregate=='mean':
        df_w = df_dw.groupby('index').mean()
    elif aggregate=='max':
        df_w = df_dw.groupby('index').max()
    elif aggregate=='median':
        df_w = df_dw.groupby('index').median()
    elif aggregate=='sum':
        df_w = df_dw.groupby('index').sum()
    return df_w

def GenDf_d2m(df_d, aggregate='last'):
    df_dm = copy.deepcopy(df_d)
    df_dm.index = [day2month(x) for x in df_dm.index]
    df_dm.index.name = 'index'
    if aggregate=='last':
        df_m = df_dm[~df_dm.index.duplicated(keep='last')]   
    if aggregate=='mean':
        df_m = df_dm.groupby('index').mean()
    elif aggregate=='max':
        df_m = df_dm.groupby('index').max()
    elif aggregate=='median':
        df_m = df_dm.groupby('index').median()
    elif aggregate=='sum':
        df_m = df_dm.groupby('index').sum()
    return df_m

def GenDf_w2m(df_w, aggregate='last'):
    df_wm = copy.deepcopy(df_w)
    df_wm.index = [day2month(week2day(x)) for x in df_wm.index]
    df_wm.index.name = 'index'
    if aggregate=='last':
        df_m = df_wm[~df_wm.index.duplicated(keep='last')]   
    if aggregate=='mean':
        df_m = df_wm.groupby('index').mean()
    elif aggregate=='max':
        df_m = df_wm.groupby('index').max()
    elif aggregate=='median':
        df_m = df_wm.groupby('index').median()
    elif aggregate=='sum':
        df_m = df_wm.groupby('index').sum()        
    return df_m

def GenDf_w2d(df_d, df_w, interpolate='linear'):

    if df_d is None:

        firstweek = df_w.index[0]
        lastweek = df_w.index[-1]

        start_dt = week2day(firstweek)
        end_dt = week2day(lastweek)

        days = uniq([x for x in datesbetween(start_dt, end_dt)])
        df_d = pd.DataFrame(index=days)


    df_wd = pd.DataFrame(index = [day2week(x) for x in df_d.index], columns = df_w.columns)
    df_wd_index = np.array([int(x) for x in df_wd.index])
    week_loc = np.where([x>0 for x in df_wd_index[1:] - df_wd_index[:-1]]+[True])[0]
    df_wd.index = df_d.index

    try:
        df_wd.iloc[week_loc] = df_w.loc[[str(x) for x in df_wd_index[week_loc]],:]
    except:
        for m in week_loc:
            try:
                df_wd.iloc[m] = df_w.loc[str(df_wd_index[m]),:]
            except:
                continue

    if interpolate=='linear':
        return df_wd.apply(pd.to_numeric).interpolate('linear', limit_area='inside')
    else:
        return df_wd.apply(pd.to_numeric)

def GenDf_m2d(df_d, df_m, interpolate='linear'):

    if df_d is None:

        firstmon = df_m.index[0]
        lastmon = df_m.index[-1]

        start_dt = month2day(firstmon)
        end_dt = month2day(lastmon)

        days = uniq([x for x in datesbetween(start_dt, end_dt)])
        df_d = pd.DataFrame(index=days)


    df_md = pd.DataFrame(index = [day2month(x) for x in df_d.index], columns = df_m.columns)
    df_md_index = np.array([int(x) for x in df_md.index])
    month_loc = np.where([x>0 for x in df_md_index[1:] - df_md_index[:-1]]+[True])[0]
    df_md.index = df_d.index

    try:
        df_md.iloc[month_loc] = df_m.loc[[str(x) for x in df_md_index[month_loc]],:]
    except:
        for m in month_loc:
            try:
                df_md.iloc[m] = df_m.loc[str(df_md_index[m]),:]
            except:
                continue

    if interpolate=='linear':
        return df_md.apply(pd.to_numeric).interpolate('linear', limit_area='inside')
    else:
        return df_md.apply(pd.to_numeric)        

def GenDf_m2w(df_w, df_m, interpolate='linear'):

    if df_w is None:

        firstmon = df_m.index[0]
        lastmon = df_m.index[-1]

        start_dt = firstdate(firstmon[:4],firstmon[4:])
        end_dt = lastdate(lastmon[:4],lastmon[4:])

        weeks = uniq([day2week(x) for x in datesbetween(start_dt, end_dt)])
        df_w = pd.DataFrame(index=weeks)


    df_mw = pd.DataFrame(index = [day2month(week2day(x)) for x in df_w.index], columns = df_m.columns)
    df_mw_index = np.array([int(x) for x in df_mw.index])
    month_loc = np.where([x>0 for x in df_mw_index[1:] - df_mw_index[:-1]]+[True])[0]
    df_mw.index = df_w.index

    try:
        df_mw.iloc[month_loc] = df_m.loc[[str(x) for x in df_mw_index[month_loc]],:]
    except:
        for m in month_loc:
            try:
                df_mw.iloc[m] = df_m.loc[str(df_mw_index[m]),:]
            except:
                continue

    if interpolate=='linear':
        return df_mw.apply(pd.to_numeric).interpolate('linear', limit_area='inside')       
    else:
        return df_mw.apply(pd.to_numeric)

def GenDf_q2m(df_q,interpolate='linear'):
    df_q.index = [str(x) for x in df_q.index]
    df_q.index = [x.replace('Q','q') for x in df_q.index]

    df_qm = pd.DataFrame(index = [str(x)+str(y+100)[-2:] for x in uniq([z[:4] for z in df_q.index]) for y in range(1,13)], 
                        columns = df_q.columns)
    df_qm = df_qm.loc[quarter2month(df_q.index[0]):quarter2month(df_q.index[-1])]
    quarter_loc = np.where([x[-2:] in ('03','06','09','12') for x in df_qm.index])[0]

    try:
        df_qm.iloc[quarter_loc] = df_q.loc[[month2quarter(x) for x in df_qm.index[quarter_loc]],:]
    except:
        for q in quarter_loc:
            try:
                df_qm.iloc[q] = df_q.loc[month2quarter(df_qm.index[q]),:]
            except:
                continue

    if interpolate=='linear':
        return df_qm.apply(pd.to_numeric).interpolate('linear', limit_area='inside')       
    else:
        return df_qm.apply(pd.to_numeric)

def GenDf_m2q(df_m, aggregate='last'):
    df_mq = copy.deepcopy(df_m)
    df_mq.index = [month2quarter(x) for x in df_mq.index]
    df_mq.index.name = 'index'
    if aggregate=='last':
        df_q = df_mq[~df_mq.index.duplicated(keep='last')]   
    if aggregate=='mean':
        df_q = df_mq.groupby('index').mean()
    elif aggregate=='max':
        df_q = df_mq.groupby('index').max()
    elif aggregate=='median':
        df_q = df_mq.groupby('index').median()
    elif aggregate=='sum':
        df_q = df_mq.groupby('index').sum()
    return df_q

def GenDf_m2y(df_m, aggregate='last'):
    df_my = copy.deepcopy(df_m)
    df_my.index = [str(x)[:4] for x in df_my.index]
    df_my.index.name = 'index'
    if aggregate=='last':
        df_y = df_my[~df_my.index.duplicated(keep='last')]   
    if aggregate=='mean':
        df_y = df_my.groupby('index').mean()
    elif aggregate=='max':
        df_y = df_my.groupby('index').max()
    elif aggregate=='median':
        df_y = df_my.groupby('index').median()
    elif aggregate=='sum':
        df_y = df_my.groupby('index').sum()
    return df_y

def GenDf_y2m(df_y,interpolate='linear'):
    df_y.index = [str(x) for x in df_y.index]
    df_ym = pd.DataFrame(index = [str(x)+str(y+100)[-2:] for x in df_y.index for y in range(1,13)], columns = df_y.columns)
    df_ym_index = np.array([int(x[:4]) for x in df_ym.index])
    year_loc = np.where([x>0 for x in df_ym_index[1:] - df_ym_index[:-1]]+[True])[0]

    try:
        df_ym.iloc[year_loc] = df_y.loc[[str(x) for x in df_ym_index[year_loc]],:]
    except:
        for y in year_loc:
            try:
                df_ym.iloc[y] = df_y.loc[str(df_ym_index[y]),:]
            except:
                continue

    if interpolate=='linear':
        return df_ym.apply(pd.to_numeric).interpolate('linear', limit_area='inside')       
    else:
        return df_ym.apply(pd.to_numeric)

def GenMonthDummy(index, MW='week', num_month=13):
    if MW == 'week':
        month_dummy = pd.get_dummies([int(day2month(week2day(x))[-2:]) for x in index])
        month_dummy.index = index
        # month_dummy = pd.DataFrame(0,index = index, columns = range(1,num_month))
        # for i,m in enumerate([int(day2month(week2day(x))[-2:]) for x in month_dummy.index]):
        #     month_dummy.loc[month_dummy.index[i],m] = 1
    elif MW == 'month':
        month_dummy = pd.get_dummies([int(x[-2:]) for x in index])
        month_dummy.index = index
        # month_dummy = pd.DataFrame(0,index = index, columns = range(1,num_month))
        # for i,m in enumerate([int(x[-2:]) for x in month_dummy.index]):
        #     month_dummy.loc[month_dummy.index[i],m] = 1

    month_dummy.columns = [str(x) for x in month_dummy.columns]
    return month_dummy

def GenYearDummy(index, MW='week'):
    year_dummy = pd.get_dummies([x[:4] for x in index])
    year_dummy.index = index
    year_dummy.columns = [str(x) for x in year_dummy.columns]
    return year_dummy
    # year_dummy = pd.DataFrame(index = index)
    # for i,y in enumerate(np.unique([x[:4] for x in index])):
    #     year_dummy = pd.concat([year_dummy, \
    #                             pd.DataFrame(1,index=[x for x in index if str(x[:4])==str(y)], \
    #                                          columns=[str(y)])],\
    #                            axis=1)
    # year_dummy.columns = [str(x) for x in year_dummy.columns]
    # return year_dummy.fillna(0)

def GenStructBreakDummy(index, time, time2=None, MW='week'):
    if MW == 'week':
        structbreak_dummy = pd.DataFrame(0,index = index, columns = ['sb'])
        if time2 is None:
            structbreak_dummy.loc[structbreak_dummy.index>=str(time),'sb'] = 1
        else:
            structbreak_dummy.loc[(structbreak_dummy.index>=str(time)) & (structbreak_dummy.index<=str(time2)),'sb'] = 1
    elif MW == 'month':
        structbreak_dummy = pd.DataFrame(0,index = index, columns = ['sb'])
        if time2 is None:
            structbreak_dummy.loc[structbreak_dummy.index>=str(time),'sb'] = 1
        else:
            structbreak_dummy.loc[(structbreak_dummy.index>=str(time)) & (structbreak_dummy.index<=str(time2)),'sb'] = 1        

    structbreak_dummy.columns = [str(x) for x in structbreak_dummy.columns]
    return structbreak_dummy
    
def GenCountDummy(index, holiday, holiday_counts):
    holiday_dummy = pd.DataFrame(0,index=index,columns=['h'])
    for i,h in enumerate(holiday):
        holiday_dummy.loc[h,'h'] = holiday_counts[i]
    holiday_dummy = holiday_dummy.loc[index]
    return holiday_dummy
    
# data check fuction    

def uniq(ls):
    seen = set()
    uniq = [x for x in ls if x not in seen and not seen.add(x)]   
    return uniq
    
def dupes(ls):
    seen = set()
    dupes = [x for x in ls if x in seen or seen.add(x)]  
    return dupes



#criteria functions

def rmse(y_pred,y_true): return np.sqrt(np.mean((y_pred-y_true)**2))

def mae(y_pred,y_true): return np.mean(np.abs(y_pred-y_true))



#transformation functions

def x13as(df, period='M', X12PATH='D:/x1.programs/x13as/'):
    df.dropna(inplace=True)    
    ind = df.index 
    col = df.columns[0]
    df.index = pd.PeriodIndex(df.index, freq=period)
    df.columns = ['temp']
    df = x13_arima_analysis(df, x12path=X12PATH).seasadj.to_frame(col)
    df.index = ind
    return df

def hp(df, period='M', lamb=None):
    if lamb != None:
        return hpfilter(x, lamb=lamb)
    if period == 'D':
        lamb = 1600*((365/4)**4)
    elif period == 'W':
        lamb = 1600*((52/4)**4)
    elif period == 'M':
        lamb = 129600 # or 14400
    elif period == 'Q':
        lamb = 1600
    elif period == 'Y':
        lamb = 6.25 # 100 for half-yearly
    return hpfilter(df, lamb=lamb)

def extrapolate(df, maxlags=1):
    df_ = df.copy()
    df = copy.deepcopy(df.loc[df.dropna(axis=0).index[0]:])
    
    if df.isna().sum().sum() == 0:
        return df
    
    if df.shape[1] == 1:
        df_train = df.dropna()
        df_test = df[df.isna().sum(axis=1)>0]
        
        df_test[df_test.columns[0]] = AutoReg(endog=df_train, lags=maxlags)\
                                      .fit().forecast(df_test.shape[0]).values
        df.loc[df_test.index] = df_test
        df_.loc[df.index] = df
        return df_
    else:
        col_id_nan = np.where(df.dropna(axis=0,how='all').isna().sum(axis=0)>0)[0]
        for i in col_id_nan:
            df_train = df.dropna()
            df_test = df[df.iloc[:,i].isna()]

            forc = AutoReg(endog=df_train.iloc[:,[i]],\
                           exog=df_train.drop(df_train.columns[col_id_nan], axis=1), lags=maxlags)\
                           .fit().forecast(df_test.shape[0],\
                           exog=df_test.drop(df_train.columns[col_id_nan], axis=1)).values
            df.iloc[:,i].loc[df_test.index] = forc
        df_.loc[df.index] = df

        # df_train = df.dropna()
        # df_test = df[df.isna().sum(axis=1)>0]
        
        # df_test[df_test.columns[0]] = AutoReg(endog=df_train.iloc[:,[0]],\
        #                                exog=df_train.iloc[:,1:], lags=maxlags)\
        #                                .fit().forecast(df_test.shape[0],\
        #                                exog=df_test.iloc[:,1:]).values
        # df.loc[df_test.index] = df_test
        # df_.loc[df.index] = df
        return df_

def proportion(df):
    return (df.T/df.sum(axis=1)*100).T

def contribution(df, period=12):
    # return (df.T/df.shift(period).sum(axis=1).T).T
    return ((df-df.shift(period)).T/df.shift(period).sum(axis=1)).T

def contribution_proportion(df, period=12):    
    return ((df-df.shift(period)).T/(df.sum(axis=1)-df.shift(period).sum(axis=1))).T

def norm(pdx): return (pdx-pdx.mean())/pdx.std()
def scale(pdx): return (pdx-pdx.min())/(pdx.max()-pdx.min())
def linintp(pdx): return pdx.interpolate(method='linear')
def hptrend(lst,lamb=1): return pd.DataFrame(hpfilter(lst, lamb=lamb)[1])
def hpcycle(lst,lamb=1): return pd.DataFrame(hpfilter(lst, lamb=lamb)[0])
# def hmtrend(lst, hint=12): return qe.hamilton_filter(lst.values, hint)[1]
# def hmcycle(lst, hint=12): return qe.hamilton_filter(lst.values, hint)[0]

def unnorm(pdx,m,s): return pdx*s+m


def ifexist(df, var, error_return=None):
    if type(df)==dict:
        if var in df.keys():
            return df[var]
        else:
            return error_return
    elif type(df)==pd.DataFrame:
        if var in df.columns:
            return df[var]
        else:
            return error_return

#memory functions

def sizeof_fmt(num, suffix='B'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

# plotting functions

def Hangul(fontpath = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'):
    from matplotlib.font_manager import fontManager, FontProperties
    from matplotlib import rcParams

    fontManager.addfont(fontpath)
    fontprop = FontProperties(fname=fontpath, size=10)
    fontname = fontprop.get_name()

    rcParams['font.family'] = fontname
    rcParams['axes.unicode_minus'] =False

def strindex(df):
    df.index = [str(x) for x in df.index]
    return df

def Plotly(df, color=None, theme=None, dropdown=False, return_fig=False):
    pd.options.plotting.backend = "plotly"

    df.index = [str(x) for x in df.index]

    if color is not None:
        fig = df.plot(color_discrete_map=color)
    else:
        fig = df.plot()

    myupdatemenus=[
        dict(
            type = "buttons",
            buttons=list([
                dict(
                    args=["visible", "legendonly"],
                    label="Deselect All",
                    method="restyle"
                ),
                dict(
                    args=["visible", True],
                    label="Select All",
                    method="restyle"
                )
            ]),
            direction = "right",                                
            showactive= True,                                
            pad={"r": 10, "t": 10},
            x=0.9,
            xanchor="left",
            y=1.12,
            yanchor="top"
        ),
    ]
    fig.update_layout(dict(updatemenus = myupdatemenus))
    
    if theme=='white':
        fig.update_layout(
            plot_bgcolor='white'
        )
        fig.update_xaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='lightgrey'
        )
        fig.update_yaxes(
            mirror=True,
            ticks='outside',
            showline=True,
            linecolor='black',
            gridcolor='lightgrey'
        )
        fig.update_layout(
            xaxis_title="", yaxis_title=""
        )
        
    if dropdown:
        add1updatemenus = [
            dict(buttons= [dict(
                        method= 'restyle',
                        label= str(i),
                        args= [{'x':[[z for z in df[y].index if int(z)>=int(i)] for y in df],
                                'y': [df[y][[z for z in df[y].index if int(z)>=int(i)]] for y in df]}]
                        ) for i in df.index],
            direction= 'down',
            showactive= True,
            pad={"r": 10, "t": 10},
            x=0.0,
            xanchor="left",
            y=1.12,
            yanchor="top"                
                )
        ]
        add2updatemenus = [
            dict(buttons= [dict(
                        method= 'restyle',
                        label= str(i),
                        args= [{'x':[[z for z in df[y].index if int(z)<=int(i)] for y in df],
                                'y': [df[y][[z for z in df[y].index if int(z)<=int(i)]] for y in df]}]
                        ) for i in df.index],
            direction= 'down',
            showactive= True,
            pad={"r": 10, "t": 10},
            x=0.15,
            xanchor="left",
            y=1.12,
            yanchor="top"                
                )
        ]
        
        
        fig.update_layout(dict(updatemenus = myupdatemenus+add1updatemenus+add2updatemenus))
        pass

    if return_fig:
        return fig
    else:
        fig.show()

def plotly_theme(fig, legend_x=0.65, legend_y=0.05, fs=20, legend_orientation='v', fs_legend=None, \
                tickangle_x=90, title_x=None, title_y=None, range_y=None, margin=dict(l=10, r=30, t=30, b=10),\
                left_unit=None, right_unit=None ):

    if fs_legend is None:
        fs_legend = fs

    fig.update_layout(
        legend=dict(
            x=legend_x,
            y=legend_y,
            traceorder="normal",
            title=None,
            orientation=legend_orientation,
            font=dict(
                size=fs_legend,
                #family="sans-serif",
                #color="black"
            ),
        )
    )
    fig.update_layout(
        margin=margin,
        plot_bgcolor='white',
        font=dict(size=fs)
    )
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        tickangle=tickangle_x,
        #gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        #gridcolor='lightgrey'
    )
    fig.update_layout(
        xaxis_title=title_x,
        yaxis_title=title_y,
    )
    if range_y is not None:
        fig.update_yaxes(
            range=range_y
        )

    if left_unit is not None:
        fig.add_annotation(dict(font=dict(color="black",size=left_unit.get('fs', fs)),
                                x=0, y=1.01,
                                showarrow=False,
                                text=left_unit['text'],
                                xanchor='left',
                                yanchor='bottom',
                                textangle=0,
                                xref="paper",
                                yref="paper"
                               ))        

    if right_unit is not None:
        fig.add_annotation(dict(font=dict(color="black",size=right_unit.get('fs', fs)),
                                x=1, y=1.01,
                                showarrow=False,
                                text=right_unit['text'],
                                xanchor='right',
                                yanchor='bottom',
                                textangle=0,
                                xref="paper",
                                yref="paper"
                               ))         
        
    # fig.add_trace(go.Scatter(
    #     x=[-1],
    #     y=[1.5],
    #     mode="text",
    #     name="",
    #     text=["(%p)"],
    #     textposition="top center"
    # ))
    # fig.show()