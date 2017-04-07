from django.shortcuts import render
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import QueryForm
from .models import Result
import pandas as pd
import requests
import datetime
import math
import pickle

# 検索ページへ遷移
def top(request):
    return render(request,'search.html')

# 検索処理・検索結果を返す
def search(request):
    if len(request.POST.dict()) > 0:
        if request.method == 'POST':
            form = QueryForm(request.POST)
            dateFrom = form['dateFrom'].value()
            dateTo = form['dateTo'].value()
            keyword = form['keyword'].value()

            # 日付(from)が日付(To)より未来の場合, 結果を返さず
            # 検索画面へ遷移する
            if dateFrom > dateTo:
                msg = 'dateReverse'
                return render(request,'search.html',{'error':msg})
            else:
                # 検索対象の年月日を取得する
                ymd = dateComplete(dateFrom,dateTo)

            if form['searchType'].value() == 'and':
                payload={'ymd':ymd,'keyword':keyword,'count':'100','order':'2'}
            else:
                payload={'ymd':ymd,'keyword_or':keyword,'count':'100','order':'2'}

        allEvents = []
        resultList = []
        connpass = ConnpassAPI(payload)
        if connpass.resultsNum() < 1:
            msg = 'noResult'
            return render(request,'search.html',{'error':msg})
        allEvents = connpass.allEventsInfo()


        for idx,item in allEvents.iteritems():
            title = item['title']
            URL = item['event_url']
            hashTag = item['hash_tag']
            start = item['started_at']
            end = item['ended_at']
            limit = item['limit']
            accepted = item['accepted']
            waiting = item['waiting']
            address = item['address']
            place = item['place']
            if item['series'] is not None:
                groupNm = item['series']['title']
                groupUrl = item['series']['url']
            else:
                groupNm = " "
                groupUrl = " "
            data = {
                'keyword':keyword,
                'from':dateFrom,
                'to':dateTo,
                'title':title,
                'URL':URL,
                'start':start,
                'end':end,
                'limit':limit,
                'accepted':accepted,
                'waiting':waiting,
                'address':address,
                'place':place,
                'groupNm':groupNm,
                'groupUrl':groupUrl}
            result = Result(data)
            resultList.append(result)

        # 検索結果は開催日降順で返ってくるので,要素の逆順にすることで開催日昇順にする
        resultsReverse = resultList[::-1]
        request.session.setdefault('results',resultsReverse)

    res = request.session['results']
    paginator = Paginator(res,15)
    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    return render(request,'results.html',{'results':results})

# 入力された2つの日付の間を補完する
def dateComplete(dateFrom,dateTo):

    # Connpass APIの日付仕様に合わせて/を削除
    dateFrom = dateFrom.replace('/','')
    dateTo = dateTo.replace('/','')

    d_from = datetime.datetime.strptime(dateFrom,'%Y%m%d')
    d_to = datetime.datetime.strptime(dateTo,'%Y%m%d')

    dates = []

    # 検索対象年月日(from)をリストへ
    dates.append(dateFrom)

    # 検索対象日from,toの間を補完する
    while(d_from != d_to):
        d_from += datetime.timedelta(days=1)
        dates.append(d_from.strftime('%Y%m%d'))
    return dates

# Connpass API
class ConnpassAPI:
    __url = 'https://connpass.com/api/v1/event/'

    def __init__(self,payload):
        self.payload = payload

    def __fetch(self):
        self.res = pd.DataFrame.from_dict(requests.get(self.__url,params=self.payload).json())
        return self.res

    # 検索結果の総件数を返す
    def resultsNum(self):
        df = self.__fetch().drop('events',axis=1)
        if df.empty:
            return 0
        else:
            return df[0:1]['results_available'][0]

    '''
    イベント詳細(全件)を返す
    戻り値:pandas.series
    '''
    def allEventsInfo(self):
        available = self.resultsNum()
        eventInfo = pd.DataFrame()
        iterate = math.ceil(available/100)
        for each in range(iterate):
            if each > 1:
                self.payload['start'] = (iterate*100)+1
                df = pd.DataFrame.from_dict(self.__fetch())
                eventInfo = pd.concat([eventInfo,df],ignore_index=True)
            else:
                eventInfo = pd.DataFrame.from_dict(self.__fetch())
        return eventInfo['events']
