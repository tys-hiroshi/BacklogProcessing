# -*- coding:utf-8 -*-

class TimeUtils():
    @staticmethod
    def utc(dateString):
        ''' ISO 8601の、UTCを示す末尾の 'Z' を、'+0000' に置き換える
        '''
        if dateString.endswith('Z'):
            dateString = dateString.replace('Z', '+0000')
        return dateString

