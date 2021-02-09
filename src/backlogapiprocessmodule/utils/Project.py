#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from backlogapiprocessmodule.utils.Issue import Issue
from datetime import datetime, timedelta
from pytz import timezone
import copy

class Project(object):
    ''' projectを抽象化するクラス
    '''
    def __init__(self, projectKey, client, logger):
        self.project = None
        projects = client.projects()
        for project in projects:
            print(f"projectKey: {projectKey}")
            if project['projectKey'] == projectKey:
                self.project = project
                break
        if self.project is None:
            raise Exception(f'project not found: projectKey = {projectKey}')

        self.client = client
        self.logger = logger
        self.issues = None

    # private
    def getIssueTypeId(self, issueTypeName):
        issueTypes = self.client.project_issue_types(self.project['id'])

        issueTypeId = None
        for issueType in issueTypes:

            if not 'name' in issueType:
                continue

            name = issueType['name']
            if name != issueTypeName:
                continue

            issueTypeId = issueType['id']
            break

        return issueTypeId

    # private
    def getIssueKeys(self, issueTypeId, beginDateStr, endDateStr, operationType, maxCount):
        self.logger.info("---------------------operationType: {}---------------------".format(operationType))
        params = {
            'projectId[]': [self.project['id']],
            'issueTypeId[]': [issueTypeId],
            'sort': 'updated',
            'order': 'desc'
        }
        # maxCountが負の値の場合は、'count' を明示的に指定しない
        if maxCount >= 0:
            params['count'] = maxCount
        beginDate = datetime.strptime(beginDateStr, '%Y-%m-%d')   
        endDate = datetime.strptime(endDateStr, '%Y-%m-%d')

        datetime_now = datetime.now(timezone('UTC'))  ## NOTE: maybe backlog datetime is UTC
        until_request_day = endDate.day if(datetime_now.day > 25) else datetime_now.day + 1  ## adding 1 day is buffer
        issueKeys = []
        for day in range(1, until_request_day):  ##NOTE: api request for until_request_day. endDate.day is waste request.
            self.logger.info(f"request day: {day}")
            sinceDate = datetime(beginDate.year, beginDate.month, day)
            # delta = timedelta(days=1)
            # untilDate = sinceDate + delta
            # if sinceDate.month != untilDate.month:
            #     untilDate = sinceDate
            if sinceDate.month != beginDate.month:
                break
            sinceDateStr = sinceDate.strftime('%Y-%m-%d')
            params[f'{operationType}Since'] = sinceDateStr
            params[f'{operationType}Until'] = sinceDateStr
            issues = self.client.issues(params)
            self.logger.info(f"sinceDate: {sinceDate}; len(issues): {len(issues)}")
            if len(issues) == maxCount:
                self.logger.info(f"!!!!!WARNING!!!!! len(issues): {maxCount}; start get issues per statusId.")
                statues = self.getProjectStatuses(self.project['id'])
                # add status condition
                for status in statues:
                    self.logger.info(f"!!!!!WARNING!!!!! status name: {status['name']}")
                    tmpparams = copy.deepcopy(params)
                    tmpparams['statusId[]'] = status["id"]
                    issues = self.client.issues(tmpparams)
                    self.logger.info(f"len(issues): {len(issues)};")
                    if len(issues) == maxCount:
                        self.logger.info(f"!!!!!ERROR!!!!! len(issues): {len(issues)}; should add conditions.")
                    issueKeys = self.joinIssueKeys(issueKeys, issues)
            else:
                issueKeys = self.joinIssueKeys(issueKeys, issues)

        issueKeys = sorted(set(issueKeys), key=issueKeys.index)  ## distinct
        ## NOTE: for debug
        # issueKeysOrderbyKey = sorted(issueKeys)
        # for issueKey in issueKeysOrderbyKey:
        #     self.logger.info(f"issueKey: {issueKey}")
        return issueKeys
    
    def joinIssueKeys(self, issueKeys, issues):
        for issue in issues:
            self.logger.info("issueKey: {}; created: {}; updated: {};".format(issue['issueKey'], issue['created'], issue['updated']))
            issueKeys += [issue['issueKey']]
        return issueKeys

    def getProjectStatuses(self, projectId):
        ## NOTE: 本当は pybacklog を使いたいが PullReuqestしたが Mergeされないので、自分でリクエストする
        ## NOTE: 本当は これを使いたい。 return self.client.project_statuses(project_id_or_key)
        #メソッド: GET 
        #URL: /api/v2/projects/:projectIdOrKey/statusesreturn self.do
        return self.client.do("GET", "projects/{project_id_or_key}/statuses", url_params={"project_id_or_key": projectId})
    
    def collectIssues(self, issueTypeNameList: list, beginDate, endDate, maxCount=-1):
        self.logger.info(f"collectIssues: projectKey: {self.project['projectKey']}")
        issues = []  ## ProjectKeyに対するIssue
        for issueTypeName in issueTypeNameList:
            issueTypeId = self.getIssueTypeId(issueTypeName)
            if not issueTypeId: # 指定されたissue typeがこのprojectに存在しない
                continue

            createdIssueKeys = self.getIssueKeys(issueTypeId, beginDate, endDate, 'created', maxCount)
            updatedIssueKeys = self.getIssueKeys(issueTypeId, beginDate, endDate, 'updated', maxCount)
            self.logger.info(f'----------------------- len(createdIssueKeys): {len(createdIssueKeys)}, len(updatedIssueKeys): {len(updatedIssueKeys)}')
            issueKeys = createdIssueKeys + updatedIssueKeys
            issueKeys = list(set(issueKeys))
            issueKeys.sort()
            self.logger.info(f'----------------------- len(issueKeys): {len(issueKeys)}')

            for issueKey in issueKeys:
                issues += [Issue(issueKey, self.client, self.logger, beginDate, endDate)]
        self.issues = issues

    def getSummaryRecord(self, maxComments):
        if self.issues is None:
            ## NOTE: exception だったが更新されないすべてのProjectで課題が一件も更新されないことはあるのでログに修正
            self.logger.error('issues have not been collected yet, call collectIssues() first')

        hours = 0.0
        for issue in self.issues:
            actualHours = issue.getActualHours(maxComments)
            self.logger.debug(f'actualHours: {actualHours}')
            hours += actualHours[1]
        return (self.project['name'], self.project['projectKey'], hours)

    def getDetailRecords(self, maxComments):
        if self.issues is None:
            ## NOTE: exception だったが更新されないすべてのProjectで課題が一件も更新されないことはあるのでログに修正
            self.logger.error('issues have not been collected yet, call collectIssues() first')

        records = []
        for issue in self.issues:
            actualHours = issue.getActualHours(maxComments)
            self.logger.debug(f'actualHours: {actualHours}')
            records.append(actualHours)
        return (self.project['name'], self.project['projectKey'], records)

if __name__ == '__main__':
    pass
