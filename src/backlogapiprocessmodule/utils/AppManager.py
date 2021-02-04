#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pybacklog import BacklogClient
from backlogapiprocessmodule.utils.Project import Project
from backlogapiprocessmodule.utils.Summary import Summary
from backlogapiprocessmodule.utils.Detail import Detail

class AppManager(object):
    ''' このアプリケーションのクラス
    '''
    def __init__(self, config, logger):
        self.client = BacklogClient(config['WIKI_SPACE'], config['API_KEY']['GLOBAL'])
        self.projects = []
        self.logger = logger
        for projectKey in config['PROCESSING_PROJECT_KEY']:
            self.projects.append(Project(projectKey, self.client, logger))

    def collectIssues(self, issueTypeNameList: list, beginDate, endDate, maxCount):
        for project in self.projects:
            project.collectIssues(issueTypeNameList, beginDate, endDate, maxCount)

    def reportSummary(self, wikiId, period, maxComments, isUpdateWiki = False):
        summary = Summary(wikiId, self.client, self.logger)
        record = {}
        for project in self.projects:
            rec = project.getSummaryRecord(maxComments)
            record[rec[1]] = (rec[2], rec[0])
        summary.addRecord(period, record).printRecords(isUpdateWiki)

    def reportDetail(self, wikiId, period, maxComments, isUpdateWiki = False):
        detail = Detail(wikiId, self.client, self.logger)
        projects = {}
        for project in self.projects:
            records = project.getDetailRecords(maxComments)
            label = f'{records[0]} ({records[1]})'
            projects[label] = records[2]
        detail.addSection(period, projects).printSections(isUpdateWiki)

if __name__ == '__main__':
    pass
