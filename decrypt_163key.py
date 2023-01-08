#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Thank you so much, https://github.com/lycode404/163KeyDecrypter/ !
163key解码器
在网易云下载的音乐文件都会带有以“163 key(Don't modify):”开头的注释，后面是经过加密的json代码。
只需要输入“163 key(Don't modify):”后面的一串代码，本程序即可解密出对应的json文本。
解码流程：163key→Base64解码→AES-128-ECB解密→json代码
'''
from Crypto.Cipher import AES
import base64
import os

# 解密
def decrypt(data):
	key = '#14ljk_!\]&0U<\'('.encode('utf-8')
	mode = AES.MODE_ECB
	cryptor = AES.new(key, mode)
	dcdata = cryptor.decrypt(data)
	return dcdata

def mainReal(key):
	encdata = base64.b64decode(key.encode('utf-8'))
	decstr = decrypt(encdata).decode('utf-8')
	return decstr
	
def main(comment):
	comment=str(comment)
	if comment.startswith("163 key(Don\'t modify):"):
		key=comment.split("163 key(Don\'t modify):")[1]
		return mainReal(key)
	else:
		return comment

if __name__ == '__main__':
    key = input('163 key(Don\'t modify):')
    mainReal(key)

