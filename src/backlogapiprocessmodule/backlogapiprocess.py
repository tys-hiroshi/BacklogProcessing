#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from backlogapiprocessmodule.utils.Config import Config
from backlogapiprocessmodule.utils.Logger import Logger
from backlogapiprocessmodule.utils.AppManager import AppManager
from distutils.util import strtobool

#print(sys.prefix)
#print(sys.path)

#ConfigFile = 'config.yml'
#LogConfigFile = 'logging_debug.conf'

def run(configFile = 'config.yml', logConfigFile = 'logging_debug.conf'):
    def doProcessing(day, config, logger):
        beginDate = datetime(day.year, day.month, 1)
        endDate = datetime(day.year, day.month, 1) + relativedelta(months=1) - relativedelta(days=1)
        beginDate = beginDate.strftime('%Y-%m-%d')
        endDate = endDate.strftime('%Y-%m-%d')
        logger.info(f'start processing: beginDate = {beginDate}, endDate={endDate}')

        app = AppManager(config, logger)
        maxCount = 100 # backlog APIとしての上限が、現状はこの値らしい
        maxComments = 100 # backlog APIとしての上限が、現状はこの値らしい
        periodLabel = f'{beginDate} 〜 {endDate}'
        app.collectIssues(config['PROCESSING_ISSUE_TYPE_NAME'], beginDate, endDate, maxCount)
        isUpdateWiki = config['PROCESSING_UPDATE_WIKI']['IS_UPDATE']
        #isUpdateWiki = strtobool(IS_UPDATE_Str if IS_UPDATE_Str != '' else "false")
        app.reportSummary(config['PROCESSING_UPDATE_WIKI']['SUMMARY_WIKI_ID'], periodLabel, maxComments, isUpdateWiki)
        app.reportDetail(config['PROCESSING_UPDATE_WIKI']['DETAIL_WIKI_ID'], periodLabel, maxComments, isUpdateWiki)

    config = Config(configFile).content
    logger = Logger(logConfigFile)

    processingDateTimeStr = config['PROCESSING_DATETIME']
    print('-----------------------------------------')
    logger.info(f'processingDateTimeStr: {processingDateTimeStr}')
    days = []
    if processingDateTimeStr == '':
        days.append(datetime.today())
    else:
        days.append(datetime.strptime(processingDateTimeStr, '%Y-%m-%d %H:%M:%S'))

    for day in days:
        doProcessing(day, config, logger)

if __name__ == '__main__':
    '''
    Usage: [python] BacklogApiProcessing.py [yyyy-mm [...]]
    '''
    logger.info('start backlogapiprocessing.')
    import sys
    #run(sys.argv)
    configFile = 'config.yml'
    logConfigFile = 'logging_debug.conf'
    run(configFile, logConfigFile)
