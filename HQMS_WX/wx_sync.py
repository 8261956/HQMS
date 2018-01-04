# -*- coding: utf-8 -*-

import hashlib
import os
import sys; sys.path.append('../')
import requests
from urlparse import urlparse
import gevent
from gevent import monkey; monkey.patch_all()
from common import config as cfg
from common.func import APIRequest


class SyncManager(object):

    def __init__(self, get_data_paras, post_data_paras):
        """同步医院内网数据到微信云端服务器
        :param get_data_paras: 从医院内网的接口获取数据时传递的参数，是一个字典
        :param post_data_paras: 向微信云端服务器的接口同步数据时传递的参数，是一个字典
        """

        self.api_url = cfg.wx_api_url
        self.get_data_paras = get_data_paras
        self.sync_url = cfg.sync_api_url
        self.post_data_paras = post_data_paras

    def get_sync_data(self):
        """通过医院内网接口获取同步的数据"""

        get_action = self.get_data_paras["action"]

        try:
            print "[%s] GET data from source" % get_action
            response = APIRequest(self.api_url, self.get_data_paras)
        except Exception as e:
            print str(e)
        else:
            print "[%s] GET %s data" % (get_action, response.pop("num"))
            self.post_data_paras.update(response)
            # print self.sync_data
        return self.post_data_paras

    def sync(self, timeout=0):
        """通过云端服务器的同步接口上传数据"""

        post_action = self.post_data_paras["action"]
        pre_data_md5 = None

        while True:
            fetched_data = self.get_sync_data()
            fetched_data_md5 = hashlib.md5(str(fetched_data)).hexdigest()
            if pre_data_md5 == fetched_data_md5:
                print "[%s] Data has no change" % post_action
                gevent.sleep(timeout)
                continue
            pre_data_md5 = fetched_data_md5
            print "[%s] POST data to weixin cloud server" % post_action
            try:
                response = APIRequest(self.sync_url, fetched_data)
            except Exception as e:
                print str(e)
            else:
                print "[%s] POST status: %s" % (post_action, response["result"])
                gevent.sleep(timeout)


def syncVisitorsData():
    """从医院内网数据库同步患者数据到微信云端服务器。"""

    get_data_paras = {"action": "getVisitorsData"}
    post_data_paras = {"action": "syncVisitorsData"}
    visitorsSyncManager = SyncManager(get_data_paras, post_data_paras)
    visitorsSyncManager.sync(timeout=30)


def syncQueueData():
    """从医院内网数据库同步队列数据到微信云端服务器。"""

    get_data_paras = {"action": "getQueueData"}
    post_data_paras = {"action": "syncQueueData"}
    queueSyncManager = SyncManager(get_data_paras, post_data_paras)
    queueSyncManager.sync(timeout=60)


def syncWorkerData():
    """从医院内网数据库同步医生数据到微信云端服务器。"""

    get_data_paras = {"action": "getWorkersData"}
    post_data_paras = {"action": "syncWorkersData"}
    workersSyncManager = SyncManager(get_data_paras, post_data_paras)
    workersSyncManager.sync(timeout=60)


def syncStationSetData():
    """从医院内网数据库同步分诊台数据到微信云端服务器。"""

    get_data_paras = {"action": "getStationSetData"}
    post_data_paras = {"action": "syncStationSetData"}
    workersSyncManager = SyncManager(get_data_paras, post_data_paras)
    workersSyncManager.sync(timeout=60)


def syncScheduleData():
    """从医院内网数据库同步排班数据到微信云端服务器。"""

    get_data_paras = {"action": "getScheduleData"}
    post_data_paras = {"action": "syncScheduleData"}
    scheduleSyncManager = SyncManager(get_data_paras, post_data_paras)
    scheduleSyncManager.sync(timeout=60)


def syncHospitalInfoData():
    """从医院内网数据库同步医院详情数据到微信云端服务器。"""

    get_data_paras = {"action": "getHospitalInfoData"}
    post_data_paras = {"action": "syncHospitalInfoData"}
    scheduleSyncManager = SyncManager(get_data_paras, post_data_paras)
    scheduleSyncManager.sync(timeout=60)


class AvatarUpload(object):

    def __init__(self):
        self.hospitalName = None

    def get_avatar_url(self):
        api_url = cfg.wx_api_url
        post_data = {"action": "getAvatarURL"}
        avatar_data = APIRequest(api_url, post_data)
        self.hospitalName = avatar_data["hospitalName"]
        avatar_url_list = avatar_data["avatarURL"]
        print avatar_url_list
        return avatar_url_list

    def upload_avatar(self, avatar_url):
        """上传医生头像"""

        avatar = requests.get(avatar_url, stream=True)
        if avatar.status_code == 200:
            with open('avatar_tmp.jpg', 'wb+') as f:
                for chunk in avatar:
                    f.write(chunk)

        filename = os.path.basename(avatar_url)
        url_parse = urlparse(cfg.sync_api_url)
        base_url = "{0}://{1}".format(url_parse.scheme, url_parse.netloc)
        upload_url = "{0}/hqueue_wx/manager/upload_avatar".format(base_url)
        with open('avatar_tmp.jpg') as f:
            files= {"image": (filename, f, 'image/png', {})}
            response = requests.post(upload_url, files=files)

        response = response.json()
        rescode = response["rescode"]
        print rescode

        return rescode

    def upload(self, timeout=0):
        pre_list = []
        while True:
            avatar_url_list = self.get_avatar_url()
            if pre_list == avatar_url_list:
                print "AvatarData has no change"
                gevent.sleep(timeout)
                continue
            upload_list = set(avatar_url_list) - set(pre_list)
            print "Avatar num need to upload: %s" % len(upload_list)
            for url in upload_list:
                rescode = self.upload_avatar(url)
                if rescode == '200':
                    print "Avatar %s upload success" % url
                else:
                    print "Avatar %s upload failed" % url
            pre_list = avatar_url_list
            gevent.sleep(timeout)


def upload_avatars():
    """从医院内网数据库上传医生头像到微信云端服务器。"""

    uploader = AvatarUpload()
    uploader.upload(60)


if __name__ == '__main__':
    threads = [
        gevent.spawn(syncHospitalInfoData),
        gevent.spawn(syncVisitorsData),
        gevent.spawn(syncQueueData),
        gevent.spawn(syncWorkerData),
        gevent.spawn(syncStationSetData),
        gevent.spawn(syncScheduleData),
        gevent.spawn(upload_avatars)

    ]
    gevent.joinall(threads)
