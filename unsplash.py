import requests
import os
import re
from time import time

class Spider:

    def __init__(self,n=10):
        self.headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        path='./download/unsplash'
        if not os.path.exists(path):
            os.mkdir(path)
            self.path=path
        else:
            self.path=path
        self.n=n
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

    def save_img(self,url):
        text=""
        try:
            r=requests.get(url,headers=self.headers,timeout=60)
            r.raise_for_status()
            text=r.content
        except Exception as e:
            print(e.args)
        finally:
            return text

    def download_img(self,url:str):
        url_split=re.split(r'\/|\?',url)
        try:
            filename=url_split[3]+'.jpg'
            if os.path.exists(self.path+'/'+filename):
                print('下载失败，文件已存在')
            else:
                with open(self.path+'/'+filename,'wb') as f:
                    f.write(self.save_img(url))
                    f.close()
                print('成功下载第%d张图片'%(self.num))
                self.num+=1
        except Exception as e:
            print(e.args)
        finally:
            pass

    def run(self):
        try:
            for i in range(1,self.n+1):
                urls=self.getImagesLinks(i)
                for url in urls:
                    self.download_img(url)
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