import sys
import os
import subprocess
import json
import random
from pathlib import Path
import shutil
import zipfile
import stat
import requests
import hashlib
import logging,uuid,urlparser

def getOssResource(rootDir, url, md5, name, headers=None):
    localFileIsRemote = False
    if readDirChecksum(os.path.join(rootDir, name)) == md5:
        localFileIsRemote = True

    if localFileIsRemote == False: #download
        print(f"download {url} ")
        file = requests.get(url, headers=headers, timeout=(10, 180))
        random_name = ''.join(str(uuid.uuid4()).split('-'))
        try:
            ext = urlparser.urlparse(url).path[urlparser.urlparse(url).path.rindex("."):]
        except:
            ext = ".zip"
        localFile = os.path.join(rootDir, f"{random_name}{ext}")
        with open(localFile, "wb") as c:
            c.write(file.content)
            c.close()
        unzipDir = os.path.join(rootDir, name)
        if os.path.exists(unzipDir):
            shutil.rmtree(unzipDir)
        print(f"unzip {url} -> {unzipDir}")
        with zipfile.ZipFile(localFile, "r") as zipf:
            zipf.extractall(unzipDir)
        writeDirChecksum(unzipDir, localFile, md5)
        os.remove(localFile)
        return True
    return False
    
def readDirChecksum(dir):
    f = os.path.join(dir, "checksum.txt")
    txt = ""
    if os.path.exists(f):
        with open(f, "r", encoding="UTF-8") as f1:
            txt = f1.read()
            f1.close()
    return txt
        
def writeDirChecksum(dir, zipFile, fmd5=None):
    if fmd5 == None:
        if os.path.exists(zipFile) == False:
            return
        with open(zipFile, 'rb') as fp:
            fdata = fp.read()
            fp.close()
        fmd5 = hashlib.md5(fdata).hexdigest()

    with open(os.path.join(dir, "checksum.txt"), "w") as f:
        f.write(fmd5)
        f.close()

def getLocalResource(rootDir):
    data = {
        # "fonts.zip.py" : "b1f190ba1cea49177eccde2eb2a6cb13",
        # "subEffect.zip.py" : "08651251e4351fd8cd5829b2ef65a8b9"
    }
    for key in data:
        fpath = os.path.join(rootDir, key)
        if os.path.exists(fpath):
            fmd5 = data[key]
            fname = key[0:key.index(".")]
            fext = key[key.index("."):]
            fdirpath = os.path.join(rootDir, fname)
            if os.path.exists(fdirpath) and fmd5 != readDirChecksum(fdirpath):
                logging.info(f"remove old {fdirpath}")
                shutil.rmtree(fdirpath)
                with zipfile.ZipFile(fpath, "r") as zipf:
                    zipf.extractall(fdirpath)
                writeDirChecksum(fdirpath, fpath, fmd5)

checked = False
def updateBin(rootDir):
    global checked
    if checked:
        return
    checked = True
    def cp_skymedia_res(s, t):
        src = os.path.join(rootDir, s)
        if os.path.exists(src) == False:
            return
        dst = os.path.join(rootDir, "skymedia","effects",t)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    if sys.platform == "win32":
        getOssResource(rootDir, "https://oss.zjtemplate.com/res/ffmpeg_win.zip", "f395126235f961f4ab4aba6c6dab06ff", "ffmpeg")
    elif sys.platform == "linux":
        getOssResource(rootDir, "https://oss.zjtemplate.com/res/ffmpeg_linux.zip", "55a8e846b1dff9bef5350d24b11381db", "ffmpeg")
    elif sys.platform == "darwin":
        getOssResource(rootDir, "https://oss.zjtemplate.com/res/ffmpeg_darwin.zip", "ba47179e563267332f495100a89f3227", "ffmpeg")
    getOssResource(rootDir, "https://oss.zjtemplate.com/res/subEffect.zip", "08651251e4351fd8cd5829b2ef65a8b9", "subEffect")
    getOssResource(rootDir, "https://oss.zjtemplate.com/res/fonts.zip", "b1f190ba1cea49177eccde2eb2a6cb13", "fonts")
    if getOssResource(rootDir, "https://oss.zjtemplate.com/res/effect_text_20250409.zip", "db8c07aac38c3e8f009cf8e4df3fe7a2", "effect_text"):
        cp_skymedia_res("effect_text", "text")
    if getOssResource(rootDir, "https://oss.zjtemplate.com/res/effect_transition_20250409.zip", "aa2f0df808fdedd8c0795fc9b6da28a2", "effect_transition"):
        cp_skymedia_res("effect_transition", "transition")
    if getOssResource(rootDir, "https://oss.zjtemplate.com/res/effect_video_20250409.zip", "2a456c7a0d3ceae1fddfef4fc373b7c6", "effect_video"):
        cp_skymedia_res("effect_video", "video")
    if getOssResource(rootDir, "https://oss.zjtemplate.com/res/effect_blend_20250409.zip", "ff474faa599cc52261a7218952dc4252", "effect_blend"):
        cp_skymedia_res("effect_blend", "blend")
    if getOssResource(rootDir, "https://oss.zjtemplate.com/res/effect_mask_20250409.zip", "edde9b36e78425f5c118aa88f9791fc8", "effect_mask"):
        cp_skymedia_res("effect_mask", "mask")
    if getOssResource(rootDir, "https://oss.zjtemplate.com/res/effect_sticker_20250409.zip", "5853eb49aa08005544aafdfaf19129dd", "effect_sticker"):
        cp_skymedia_res("effect_sticker", "sticker")
    
    if sys.platform == "win32":
        asset_md5 = "653FC3A546A2DA6BA6D625AEE3E0314C"
        asset_url = "https://oss.zjtemplate.com/windows/TemplateProcess/templateprocess_1.13_20251009_034107.zip"
    elif sys.platform == "linux":
        asset_md5 = "F45BF6A2DE3D9FC2FA2B068C7F247882"
        asset_url = "https://oss.zjtemplate.com/linux/TemplateProcess/templateprocess_1.13_20251009_034107.zip"
    elif sys.platform == "darwin":
        asset_md5 = "A83D0632E64D15A0F9BCFDCA4D37D6E1"
        asset_url = "https://oss.zjtemplate.com/macos/TemplateProcess/templateprocess_1.13_20251009_034107.zip"
    extra_skymedia = False
    if getOssResource(rootDir, asset_url, asset_md5, "skymedia"):
        extra_skymedia = True
                    
    getLocalResource(rootDir)

    if extra_skymedia:
        cp_skymedia_res("effect_text", "text")
        cp_skymedia_res("effect_transition", "transition")
        cp_skymedia_res("effect_video", "video")
        cp_skymedia_res("effect_sticker", "sticker")
        cp_skymedia_res("effect_blend", "blend")
        cp_skymedia_res("effect_mask", "mask")

def initRes(downloadPath):
    if os.path.exists(downloadPath) == False:
        os.makedirs(downloadPath)
    updateBin(downloadPath)
    
def realBinPath(searchPath):
    binDir = ""
    if len(searchPath) <= 0 or os.path.exists(searchPath) == False:
        binDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
        if os.path.exists(binDir) == False:
            os.makedirs(binDir)
        updateBin(binDir)
    else:
        binDir = searchPath
    return binDir

def ffmpegPath(searchPath):
    return os.path.join(realBinPath(searchPath), "ffmpeg")
def skymediaPath(searchPath):
    return os.path.join(realBinPath(searchPath), "skymedia")
def subEffectPath(searchPath):
    return os.path.join(realBinPath(searchPath), "subEffect")
def fontPath(searchPath):
    return os.path.join(realBinPath(searchPath), "fonts")