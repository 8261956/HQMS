# -*- coding: utf-8 -*-

import sys
import web
sys.path.append("../")

urls = (
    '/(hqueue_wx/manager/account)', 'controller.WXUser.WXUserInterface',
    '/(hqueue_wx/manager/queue)', 'controller.WXQueue.WXQueueInterface',
    '/(hqueue_wx/manager/schedule)', 'controller.WXSchedule.WXScheduleInterface',
    '/(hqueue_wx/manager/worker)', 'controller.WXWorker.WXWorkerInterface',
    '/(hqueue_wx/manager/hospital)', 'controller.WXHospital.WXHospitalInterface',
    '/(hqueue_wx/manager/sync)', 'controller.syncData.SyncInterface',
    '/(hqueue_wx/manager/upload_avatar)', 'controller.syncData.AvatarUploader',
    '/hqueue_wx/test', 'Test',
)


class Test:
    def GET(self):
        return "Test OK~"

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()
else:
    application = app.wsgifunc()
