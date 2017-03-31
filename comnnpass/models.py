import math

class Result:
    def __init__(self,result):
        self.date = result['start'][0:10]
        self.From = result['from']
        self.To = result['to']
        self.keyword = result['keyword']
        self.title = result['title']
        self.URL = result['URL']
        self.start = result['start'][11:16]
        self.end = result['end'][11:16]
        if result['limit'] is not None:
            self.limit = result['limit']
        else:
            self.limit = 0
        self.accepted = result['accepted']
        self.waiting = result['waiting']
        self.address = result['address']
        self.place = result['place']
        self.groupNm = result['groupNm']
        self.groupUrl = result['groupUrl']
        if self.limit > 0:
            self.fullRate = math.ceil((self.accepted/self.limit)*100)
        else:
            self.fullRate = 0
