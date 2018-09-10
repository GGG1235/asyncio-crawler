#coding:utf8
import aiohttp
import asyncio
from pyquery import PyQuery as PQ
import os
from time import time

class Spider(object):

    def __init__(self,n=10):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        path='./download/mzitu'
        if not os.path.exists(path):
            os.mkdir(path)
            self.path=path
        else:
            self.path=path
        self.n=n
        self.num=1

    async def getURLs(self,n:int):
        url,urls='http://www.mzitu.com/page/%d/'%(n),[]
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response=await session.get(url=url,headers=self.headers,timeout=60)
                text=await response.text()
                pq=PQ(text)
                for inf in pq('[id="pins"]')('li'):
                    inf=PQ(inf)
                    dic={
                        'url':str(inf('a').attr('href')),
                        'title':str(inf('img').attr('alt'))
                    }
                    urls.append(dic)
        except Exception as e:
            print(e.args)
        finally:
            await session.close()
            return urls

    async def getHTMLText(self,url:str):
        text=""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                async with session.get(url=url,headers=self.headers,timeout=60) as r:
                    text=await r.text()
        except Exception as e:
            print(e.args)
        finally:
            await session.close()
            return text

    async def save_img(self,url:str):
        content=""
        try:
            async with aiohttp.ClientSession() as session:
                response=await session.get(url=url,headers=self.headers,timeout=60)
                content=await response.read()
        except Exception as e:
            print(e.args)
        finally:
            await session.close()
            return content

    async def getImageURLs(self,dic:dict,n=10):
        urls=[]
        try:
            for page in range(1,n+1):
                url=dic['url']+'/%d'%(page)
                text=await self.getHTMLText(url)
                pq=PQ(text)
                inf=pq('[class="main-image"]')('img')
                _dic={
                    'id':self.num,
                    'headers':{
                        'Referer': dic['url'],
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                    },
                    'url':str(inf.attr('src')),
                    'title':str(dic['title'])
                }
                self.num+=1
                urls.append(_dic)
        except Exception as e:
            print(e.args)
        finally:
            return urls

    async def download_img(self,dic:dict):
        filename=str(int(dic['id']/10)+1 if dic['id']%10!=0 else int(dic['id']/10))+dic['url'].split('/')[-1]
        try:
            if os.path.exists(self.path+'/'+filename):
                print('第%d张图片下载失败,图片已存在'%(dic['id']))
            else:
                content = await self.save_img(dic['url'])
                with open(self.path+'/'+filename,'wb') as f:
                    f.write(content)
                    f.close()
                    print('成功下载第%d张图片'%(dic['id']))
        except Exception as e:
            print(e.args,1)
        finally:
            pass

    async def do(self,n:int):
        try:
            urls = await self.getURLs(n)
            for url in urls:
                infs=await self.getImageURLs(url)
                for inf in infs:
                    self.headers=inf['headers']
                    await self.download_img(inf)
        except Exception as e:
            print(e.args)
        finally:
            pass


    def run(self):
        try:
            tasks = [asyncio.ensure_future(self.do(n)) for n in range(1,self.n+1)]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
        except Exception as e:
            print(e.args)
        finally:
            pass




def main():
    start=time()
    spider=Spider()
    spider.run()
    end=time()
    print('耗时:',end-start,'s')

if __name__ == '__main__':
    main()
