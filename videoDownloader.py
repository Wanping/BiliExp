from BiliClient import VideoDownloader
import sys, json, re

ReverseProxy = 'http://biliapi.8box.top/playerproxy' #解析接口代理

def callback(per):
    '''进度条回调'''
    hashes = '#' * int(per * 30)
    spaces = ' ' * (30 - len(hashes))
    sys.stdout.write("\rPercent: [%s] %.2f%%"%(hashes + spaces, per*100))
    sys.stdout.flush()

url = input('请输入视频链接：')
videos = VideoDownloader(url)
print(f'当前视频标题为：{videos.getTitle()}')
video_list = videos.all()
if len(video_list) == 1:
    video = video_list[0]
else:
    for ii in range(len(video_list)):
        print(f'{ii+1}. {video_list[ii]}')
    P = int(input('请输入要下载的分P序号：'))
    video = video_list[P-1]

cookie = input('是否加载账号cookie(y/n)：')
reverse = input('是否使用内部代理(可下载港澳台)(y/n)：')

if cookie.upper() == 'Y':
    with open('config/config.json','r',encoding='utf-8') as fp:
        configData = json.loads(re.sub(r'\/\*[\s\S]*?\/', '', fp.read()))
    if reverse.upper() == 'Y':
        video_stream_list = video.allStream(configData["users"][0]["cookieDatas"], reverse_proxy=ReverseProxy)
    else:
        video_stream_list = video.allStream(configData["users"][0]["cookieDatas"])
else:
    if reverse.upper() == 'Y':
        video_stream_list = video.allStream(reverse_proxy=ReverseProxy)
    else:
        video_stream_list = video.allStream()

for ii in range(len(video_stream_list)):
    print(f'{ii+1}. {video_stream_list[ii]}')
print('注：登录会员账号可能获得更高清视频流！')
P = int(input('请输入要下载的视频流序号：'))
video_stream = video_stream_list[P-1]
print('正在下载.....')
video_stream.download(callback=callback)
print('\n','结束')
input('按任意键退出')