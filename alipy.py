#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  alipy.py
@Date    :  2021/07/09
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
'''
import json
import math
import os
import sys
import time
import requests
import aigpy
import hashlib
from hashlib import sha1
from tqdm import tqdm
from xml.dom.minidom import parseString

requests.packages.urllib3.disable_warnings()

__TOKEN_PATH__ = os.path.expanduser('~') + '/alipy/token.json'
aigpy.path.mkdirs(aigpy.path.getDirName(__TOKEN_PATH__))




class ObjectAttr(object):
    def __init__(self, isfile=False, name='', size=0, path='', id=''):
        self.isfile = isfile
        self.name = name
        self.size = int(size)
        self.path = path
        self.id = id


class AliPy:
    def __init__(self):
        self.chunk_size = 10485760
        self.headers = {}
        self.driveId = ''
        self.pathIds = {}
        self.__login__()


    def __loadJsonFile__(self, path):
        try:
            with open(path, 'rb') as f:
                task = f.read().decode('utf-8')
                return json.loads(task)
        except Exception:
            return {}
        
    def __SaveJsonFile__(self, path, data):
        try:
            with open(path, 'w') as f:
                f.write(json.dumps(data))
                f.flush()
        except:
            return


    def __login__(self):
        tJson = self.__loadJsonFile__(__TOKEN_PATH__)
        token = tJson['token'] if 'token' in tJson else ''
        driveId = tJson['driveId'] if 'driveId' in tJson else ''
        
        while True:
            if token == '':
                aigpy.cmd.printW(aigpy.cmd.yellow("Enter token:"), False)
                token = input()
            if driveId == '':
                aigpy.cmd.printW(aigpy.cmd.yellow("Enter driveId:"), False)
                driveId = input()
            
            try:
                self.driveId = driveId
                data = {"refresh_token": token}
                post_json = requests.post('https://websv.aliyundrive.com/token/refresh',
                                        data=json.dumps(data),
                                        headers={'content-type': 'application/json;charset=UTF-8'},
                                        verify=False).json()
                token = post_json['refresh_token']
                self.headers = {
                    'authorization': post_json['access_token'],
                    'content-type': 'application/json;charset=UTF-8'
                }
                
                tJson['token'] = token
                tJson['driveId'] = driveId
                self.__SaveJsonFile__(__TOKEN_PATH__, tJson)
                return
                                
            except Exception as e:
                print(aigpy.cmd.red("Err:") + 'token已经失效')
                token = ''
                driveId = ''
                continue

    def list(self, parentFolderId: str = 'root', path='/') -> list:
        try:
            path = path.replace("\\", "/").strip().rstrip("/")

            requests_data = {"drive_id": self.driveId,
                             "parent_file_id": parentFolderId,
                             }
            requests_post = requests.post('https://api.aliyundrive.com/v2/file/list',
                                          data=json.dumps(requests_data),
                                          headers=self.headers,
                                          verify=False
                                          ).json()
            ret = []
            for item in requests_post['items']:
                obj = ObjectAttr()
                obj.isfile = item['type'] != 'folder'
                obj.name = item['name']
                obj.path = path
                obj.id = item['file_id']
                obj.size = item['size'] if 'size' in item else 0
                if not obj.isfile:
                    self.pathIds[path + '/' + obj.name] = obj.id
                    ret.append(obj)
                else:
                    ret.insert(0, obj)
            return ret

        except:
            return []

    def mkdir(self, folderName, parentFolderId='root') -> (bool, str):
        folderName = folderName.lstrip('/').rstrip('/')
        try:
            create_data = {
                "drive_id": self.driveId,
                "parent_file_id": parentFolderId,
                "name": folderName,
                "check_name_mode": "refuse",
                "type": "folder"
            }
            post_json = requests.post('https://api.aliyundrive.com/v2/file/create',
                                      data=json.dumps(create_data),
                                      headers=self.headers,
                                      verify=False).json()
            return True, post_json.get('file_id')
        except:
            return False, ''

    def mkdirs(self, path: str) -> (bool, str):
        path = path.replace("\\", "/").strip().rstrip("/")
        array = path.split('/')
        base = ''
        parentFolderId = 'root'
        try:
            for item in array:
                if item == '':
                    continue
                base += '/' + item
                if base in self.pathIds:
                    parentFolderId = self.pathIds[base]
                    continue

                check, pathId = self.mkdir(item, parentFolderId)
                if not check:
                    return False, ''

                self.pathIds[base] = pathId
                parentFolderId = pathId
        except:
            return False, ''
        return True, parentFolderId

    def requestUploadFile(self, filename, filesize, hashcode, parentFolderId) -> dict():
        try:
            part_info_list = []
            for i in range(0, math.ceil(filesize / self.chunk_size)):
                part_info_list.append({'part_number': i + 1})

            create_data = {
                "drive_id": self.driveId,
                "part_info_list": part_info_list,
                "parent_file_id": parentFolderId,
                "name": filename,
                "type": "file",
                "check_name_mode": "refuse",
                "size": filesize,
                "content_hash": hashcode,
                "content_hash_name": 'sha1'
            }

            requests_post_json = requests.post('https://api.aliyundrive.com/v2/file/create',
                                               data=json.dumps(create_data),
                                               headers=self.headers,
                                               verify=False).json()

            ret = {
                'success': True,
                'part_info_list': requests_post_json.get('part_info_list', []),
                'file_id': requests_post_json.get('file_id'),
                'upload_id': requests_post_json.get('upload_id'),
                'needUpload': True
            }
            if 'rapid_upload' in requests_post_json and requests_post_json['rapid_upload']:
                ret['needUpload'] = False
            if 'exist' in requests_post_json and requests_post_json['exist']:
                ret['needUpload'] = False
            return ret
        except:
            return {"success": False}

    def __readFile__(self, file_object, chunk_size=16 * 1024, total_size=10 * 1024 * 1024):
        load_size = 0
        while True:
            if load_size >= total_size:
                break
            data = file_object.read(chunk_size)
            if not data:
                break
            load_size += chunk_size
            yield data

    def __getXmlValue__(self, xml_string, tag_name):
        DOMTree = parseString(xml_string)
        DOMTree = DOMTree.documentElement
        tag = DOMTree.getElementsByTagName(tag_name)
        if len(tag) > 0:
            for node in tag[0].childNodes:
                if node.nodeType == node.TEXT_NODE:
                    return node.data
        return False

    def __gethash__(self, filepath, block_size=2 * 1024 * 1024):
        with open(filepath, 'rb') as f:
            sha1 = hashlib.sha1()
            while True:
                data = f.read(block_size)
                if not data:
                    break
                sha1.update(data)
            return sha1.hexdigest()

    def __getUploadUrl__(self, fileId, filesize, uploadId):
        try:
            part_info_list = []
            for i in range(0, math.ceil(filesize / self.chunk_size)):
                part_info_list.append({'part_number': i + 1})

            requests_data = {
                "drive_id": self.driveId,
                "file_id": fileId,
                "part_info_list": part_info_list,
                "upload_id": uploadId,
            }
            requests_post = requests.post('https://api.aliyundrive.com/v2/file/get_upload_url',
                                          data=json.dumps(requests_data),
                                          headers=self.headers,
                                          verify=False
                                          )
            requests_post_json = requests_post.json()
            return requests_post_json.get('part_info_list')
        except:
            return ''

    def uploadLoaclFile(self, localFilePath, remoteFilePath) -> bool:
        filename = os.path.basename(localFilePath)
        hashcode = self.__gethash__(localFilePath)
        filesize = os.path.getsize(localFilePath)

        descPath = aigpy.path.getDirName(remoteFilePath)
        check, parentFolderId = self.mkdirs(descPath)
        if not check:
            return False

        reqInfo = self.requestUploadFile(filename, filesize, hashcode, parentFolderId)
        if not reqInfo['success']:
            return False
        if not reqInfo['needUpload']:
            return True

        part_upload_url_list = reqInfo['part_info_list']
        file_id = reqInfo['file_id']
        upload_id = reqInfo['upload_id']

        with open(localFilePath, "rb") as f:
            part_number = 0
            with tqdm.wrapattr(f, "read", desc='正在上传【%s】' % filename, miniters=1, total=filesize, ascii=True) as fs:

                while part_number < len(part_upload_url_list):
                    upload_url = part_upload_url_list[part_number]['upload_url']
                    total_size = min(self.chunk_size, filesize)
                    fs.seek(part_number * total_size)
                    res = requests.put(url=upload_url,
                                       data=self.__readFile__(fs, 16 * 1024, total_size),
                                       verify=False,
                                       timeout=None)

                    if 400 <= res.status_code < 600:
                        common_get_xml_value = self.__getXmlValue__(res.text, 'Message')
                        if common_get_xml_value == 'Request has expired.':
                            part_upload_url_list = self.__getUploadUrl__(file_id, filesize, upload_id)
                            if part_upload_url_list == '':
                                return False
                            continue
                        common_get_xml_value = self.__getXmlValue__(res.text, 'Code')
                        if common_get_xml_value == 'PartAlreadyExist':
                            pass
                        else:
                            print(aigpy.cmd.red("Err:") + res.text)
                            res.raise_for_status()
                            return False
                    part_number += 1

        complete_data = {"drive_id": self.driveId,
                         "file_id": file_id,
                         "upload_id": upload_id
                         }
        complete_post = requests.post('https://api.aliyundrive.com/v2/file/complete', json.dumps(complete_data),
                                      headers=self.headers,
                                      verify=False
                                      )

        requests_post_json = complete_post.json()
        if 'file_id' in requests_post_json:
            return True
        else:
            return False
