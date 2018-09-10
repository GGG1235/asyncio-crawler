#coding:utf8
import asyncio
import aiohttp
import os
from time import time

class Spider(object):

    def __init__(self,uid:str):
        self.uid=uid
        self.page = 1
        self.num=1
        self.url='https://m.weibo.cn/api/container/getIndex'
        self.headers={
            'Accept': 'application/json, text/plain, */*',
            'MWeibo-Pwa': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        path='./download'
        if not os.path.exists(path):
            os.mkdir(path)
            os.chdir(path)
        else:
            os.chdir(path)
        path='./weibo'
        if not os.path.exists(path):
            os.mkdir(path)
            os.chdir(path)
        else:
            os.chdir(path)
        path='./'+self.uid
        if not os.path.exists(path):
            os.mkdir(path)
            os.chdir(path)
        else:
            os.chdir(path)
        self.path=os.getcwd()
        for i in range(3):
            os.chdir('../')


    async def getURLs(self):
        urls=[]
        try:
            self.params = {
                'uid': self.uid,
                'luicode': '10000011',
                'lfid': '230413' + self.uid + '_-_WEIBO_SECOND_PROFILE_WEIBO',
                'containerid': '107603' + self.uid,
                'page': self.page
            }
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response=await session.get(url=self.url,params=self.params,headers=self.headers,timeout=60)
                data=await response.json()
                if 'msg' in data.keys():
                    urls=[]
                else:
                    for card in data['data']['cards']:
                        if card['card_type'] == 9:
                            if 'pics' in card['mblog'].keys():
                                for pic in card['mblog']['pics']:
                                    urls.append(pic['large']['url'])
                            else:
                                continue
                        else:
                            continue
        except Exception as e:
            print(e.args)
        finally:
            await session.close()
            return urls

    async def save_img(self,url:str):
        content=""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as sesson:
                response=await sesson.get(url=url,headers=self.headers,timeout=60)
                content=await response.read()
        except Exception as e:
            print(e.args)
        finally:
            await sesson.close()
            return content

    async def donwload_img(self,url:str):
        filename=self.uid+'-'+str(self.num)+'.jpg'
        try:
            if os.path.exists(self.path+'/'+filename):
                print('%s:第%d张图片下载失败,文件已存在'%(self.uid,self.num))
            else:
                content=await self.save_img(url)
                with open(self.path+'/'+filename,'wb') as f:
                    f.write(content)
                    f.close()
                    print('%s:成功下载第%d张图片,文件名:%s'%(self.uid,self.num,filename))
                    self.num+=1
        except Exception as e:
            print(e.args)
        finally:
            pass

    async def do(self):
        try:
            while True:
                urls=await self.getURLs()
                if urls==[]:
                    break
                self.page+=1
                for url in urls:
                    await self.donwload_img(url)
            print('总共下载%d张图片' % (self.num))
        except Exception as e:
            print(e.args)
        finally:
            pass

    def run(self):
        try:
            tasks = [asyncio.ensure_future(self.do())]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
        except Exception as e:
            print(e.args)
        finally:
            pass

def main():
    while True:
        uid=input('uid:')
        start=time()
        spider=Spider(uid)
        spider.run()
        end=time()
        print('总共耗时%fs'%(end-start))

        t=input('继续?(Y/N)')
        if t in ['Y','y']:
            pass
        elif t in ['N','n']:
            break
        else:
            print('输入有误!将退出!')
            break



if __name__ == '__main__':
    main()
