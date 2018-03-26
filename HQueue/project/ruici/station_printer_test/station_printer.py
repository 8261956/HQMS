# -*- coding:utf-8 -*-

import ConfigParser
import os,sys
import json
import time
import codecs
import requests
import datetime

_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
stationID = int(_config.get("station", "stationID"))
server = _config.get("station", "server")
htmlPath = _config.get("station", "htmlPath")


urlBase = "http://" + server + "/hqueue"

headers = {
    'content-type': 'application/json',
}

class StationPrinter(object):

    def __init__(self):
        self.stationID = stationID

    def run(self):
        key = "print_stationID_{0}".format(self.stationID)

        while True:
            try:
                self.reqNewVisitor()
            except Exception,e:
                print Exception,str(e)
            time.sleep(1)
            print "runing..",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def reqNewVisitor(self):
        data = {
            'action':"getNextVisitor",
            'stationID':self.stationID,
        }
        html = requests.post(urlBase + '/main/printer',data = json.dumps(data),headers = headers)
        result = html.json()
        visitorInfo = result.get("detail")
        if visitorInfo == {}:
            return
        else:
            Printer().print2File(visitorInfo,htmlPath)

    def test(self):
        visitorInfo = {
            "stationName" : "儿科",
            "snumber" : "12",
            "queueName" : "采血1"
        }
        Printer().print2File(visitorInfo,htmlPath)

def fcopy(src_path, out_path):  
  try:  
    src = file(src_path, "r")  
    dst = file(out_path, "w")  
      
    dst.write(src.read())  
      
    src.close()  
    dst.close()  
  except Exception,e:  
    print e  

def freplace(file_path,old_str, new_str):  
  try:  
    f = open(file_path,'r+')  
    all_lines = f.readlines()  
    f.seek(0)  
    f.truncate()  
    for line in all_lines:  
      line = line.replace(old_str, new_str)  
      f.write(line)  
    f.close()  
  except Exception,e:  
    print e  


class Printer():
    def __init__(self):
        self.floderbase = self.cur_file_dir_win()

    # 获取脚本文件的当前路径
    def cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    def cur_file_dir_win(self):
        dir = self.cur_file_dir()
        win_dir = dir.replace("/", "\\") + "\\"
        print ("runing dir_win " + win_dir)
        return win_dir

    def print2File(self,visitorInfo, htmlPath):
        self.tempPath = "temp.html"
        fcopy(htmlPath,self.tempPath)
        freplace(self.tempPath,"print_stationName",visitorInfo.get("stationName","").encode("utf-8"))
        freplace(self.tempPath,"print_number",str(visitorInfo.get("snumber")))
        freplace(self.tempPath,"print_queue",visitorInfo.get("queueName","").encode("utf-8"))
        freplace(self.tempPath,"print_waitNum",str(visitorInfo.get("waitNum")))
        freplace(self.tempPath,"print_time",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print "new Visitor Info : "
        print visitorInfo.get("queueName")," " ,visitorInfo.get("snumber")
        self.runPrinter()


    def runPrinter(self):
        path = self.floderbase + self.tempPath
        cmd = self.floderbase + "printhtml.exe " + " " + "file=" + path
        print cmd
        os.chdir(self.floderbase)
        output = os.popen(cmd)
        print output
        return


if __name__ == '__main__':
    station_printer = StationPrinter()
    station_printer.run()
    #station_printer.test()
