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

    def is_integer_or_float(self, n):
        try:
            float(n)
            return True
        except ValueError:
            return False
    #TODO: 
    # 1. create issue that inputed actual hours. 
    # 2. change status
    # then not collect actual hours
    # FF_CONTACT_WPS_5-924
    def get_created_issue_actualHours(self, changeLogs, issue, created):
        created_issue_actualHours = 0.0
        cnt = 0
        for logItem in changeLogs:
            if logItem['field'] != 'actualHours':
                cnt += 1 
                continue
            self.logger.debug(f'logItem["originalValue"]: {logItem["originalValue"]}')
            first_originalValue_str = logItem["originalValue"]
            created_issue_actualHours = 0.0 if first_originalValue_str is None or first_originalValue_str is '' or not self.is_integer_or_float(first_originalValue_str) else float(first_originalValue_str)
            break
        #NOTE: if it's not find field: actualhours, set issue["actualHours"]
        if len(changeLogs) == cnt and self.beginDate <= created and created <= self.endDate:
            created_issue_actualHours = 0.0 if issue["actualHours"] == None else float(issue["actualHours"])  #NOTE: issue's actualhours
        return created_issue_actualHours

    # get Acutual hours in issue
    def getActualHours(self, maxComments):
        params = {
            'order': 'asc'
        }

        self.logger.debug(f'---- start getActualHours {self.issueKey} ----')
        if self.issueKey == "FF_ARRANGEAPP-147":
            print('------------------')
        # maxCommentsが負の値の場合は、'count' を明示的に指定しない
        if maxComments >= 0:
            params['count'] = maxComments
        issueComments = self.client.issue_comments(self.issueKey, params)

        issue = self.client.issue(self.issueKey)
        created = utils.Utils.utc(issue['created'])
        created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S%z')
        created += timedelta(hours=9) # JSTに変換する
        created_issue_actualHours = 0.0  # actual hours of created issue
        #集計期間かつ新規課題追加時のみ(コメントなし)工数を入れた場合に工数をカウントできるようにする
        if len(issueComments) == 0 and self.beginDate <= created and created <= self.endDate:  #within the period:
            issue_actualHours = 0.0 if issue["actualHours"] == None else float(issue["actualHours"])
            return self.issueKey, issue_actualHours

        actualHours = 0.0
        # actual hours of created issue
        # TODO: don't check changeLogs. maybe check all issueComments.
        # if it have no actual hours, get created issue actual hours.
        if len(issueComments) > 0:
            changeLogs = issueComments[0]['changeLog']
            target_updated = utils.Utils.utc(issueComments[0]['updated'])
            target_updated = datetime.strptime(target_updated, '%Y-%m-%dT%H:%M:%S%z')
            target_updated += timedelta(hours=9) # JSTに変換する

            self.logger.debug(f'target_updated: {target_updated}')
            if len(changeLogs) > 0 and self.beginDate <= target_updated and target_updated <= self.endDate:  #within term:
                created_issue_actualHours = self.get_created_issue_actualHours(changeLogs, issue, created)
        
        self.logger.debug(f'created_issue_actualHours: {created_issue_actualHours}')
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
                hours = newValue - originalValue

                self.logger.debug(f'hours: {hours}')
                actualHours += hours

        actualHours += created_issue_actualHours
        return self.issueKey, actualHours

if __name__ == '__main__':
    pass
