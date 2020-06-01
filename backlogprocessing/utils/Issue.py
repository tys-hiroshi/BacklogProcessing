#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
import utils.Utils

class Issue(object):
    def __init__(self, issueKey, client, logger, beginDate, endDate):
        self.issueKey = issueKey
        self.client = client
        self.logger = logger
        self.beginDate = datetime.strptime(f'{beginDate}+0900', '%Y-%m-%d%z')
        self.endDate = datetime.strptime(f'{endDate}+0900', '%Y-%m-%d%z')
        self.endDate += timedelta(days=1)

    # get Acutual hours in issue
    def getActualHours(self, maxComments):
        params = {
            'order': 'asc'
        }
        
        # maxCommentsが負の値の場合は、'count' を明示的に指定しない
        if maxComments >= 0:
            params['count'] = maxComments
        issueComments = self.client.issue_comments(self.issueKey, params)

        issue = self.client.issue(self.issueKey)
        created = utils.Utils.utc(issue['created'])
        created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S%z')
        created += timedelta(hours=9) # JSTに変換する

        #集計期間かつ新規課題追加時のみ(コメントなし)工数を入れた場合に工数をカウントできるようにする
        if len(issueComments) == 0 and self.beginDate <= created and created <= self.endDate:  #within the period:
            issue_actualHours = 0.0 if issue["actualHours"] == None else float(issue["actualHours"])
            return self.issueKey, issue_actualHours

        actualHours = 0.0
        for issueComment in issueComments:
            updated = utils.Utils.utc(issueComment['updated'])
            updated = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S%z')
            updated += timedelta(hours=9) # JSTに変換する
            self.logger.debug(f'updated: {updated}')
            if updated < self.beginDate or self.endDate < updated:  #out of term
                continue

            changeLog = issueComment['changeLog']
            for logItem in changeLog:
                if logItem['field'] != 'actualHours':
                    continue

                newValue = logItem['newValue']
                originalValue = logItem['originalValue']
                self.logger.debug(f'newValue = {newValue}, originalValue = {originalValue}')
                newValue = 0.0 if newValue is None else float(newValue)
                originalValue = 0.0 if originalValue is None or originalValue is '' else float(originalValue)
                #NOTE: 新規課題追加時とコメントで実績工数入力時にカウントできていない
                if self.beginDate <= created and created <= self.endDate:  #within the period
                    hours = newValue
                else:
                    hours = newValue - originalValue

                self.logger.debug(f'hours: {hours}')
                actualHours += hours

        return self.issueKey, actualHours

if __name__ == '__main__':
    pass
