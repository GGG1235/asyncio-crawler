import requests
import re
import os
import asyncio
import aiohttp
from time import time



class Spider:

    def __init__(self,n=10):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        path = './download/async_unsplash'
        if not os.path.exists(path):
            os.mkdir(path)
            self.path = path
        else:
            self.path = path
        self.n = n
        self.num=1

    def getImagesLinks(self,page:int):
        url='https://unsplash.com/napi/photos'
        params={
            'page': page,
            'per_page': '12',
            'order_by': 'latest'
        }
        links=[]
        try:
            r=requests.get(url=url,params=params,timeout=60)
            r.raise_for_status()
            r.encoding=r.apparent_encoding
            for data in r.json():
                links.append(data['urls']['full'])
        except Exception as e:
            print(e.args)
        finally:
            return links

    async def save_img(self,url):
        content=""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                response=await session.get(url,headers=self.headers,timeout=60)
                content=await response.read()
                await session.close()
        except Exception as e:
            print(e.args)
        finally:
            return content

    async def download_img(self,url:str):
        url_split = re.split(r'\/|\?', url)
        try:
            filename = url_split[3] + '.jpg'
            if os.path.exists(self.path + '/' + filename):
                print('下载失败，文件已存在')
            else:
                content=await self.save_img(url)
                with open(self.path + '/' + filename, 'wb') as f:
                    f.write(content)
                    f.close()
                print('成功下载第%d张图片' % (self.num))
                self.num+=1
        except Exception as e:
            print(e.args)
        finally:
            pass

    def run(self):
        try:
            for i in range(1, self.n + 1):
                urls = self.getImagesLinks(i)
                tasks=[asyncio.ensure_future(self.download_img(url)) for url in urls]
                loop=asyncio.get_event_loop()
                loop.run_until_complete(asyncio.wait(tasks))
        except Exception as e:
            print(e.args)
        finally:
            pass


def main():
    start=time()
    spider=Spider(n=1)
    spider.run()
    end=time()
    print(end-start,'s')

if __name__ == '__main__':
    main()


