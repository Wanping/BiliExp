from BiliClient import asyncbili
from .import_once import now_time
from random import randint
import logging, json, asyncio

end_time = now_time - (now_time + 28800) % 86400 + 43200 #当天中午12点
start_time = end_time - 86400

async def lottery_task(biliapi: asyncbili, 
                       task_config: dict    #配置
                       ) -> None:

    already_repost_dyid = [] #记录动态列表中自己已经转发的动态id
    try:
        async for x in biliapi.getDynamic():
            if x["desc"]["uid"] == biliapi.uid and x["desc"]["pre_dy_id"]: #记录本账号转发过的动态
                already_repost_dyid.append(x["desc"]["pre_dy_id"])
                continue

            timestamp = x["desc"]["timestamp"]
            if(timestamp > end_time):
                continue
            elif(timestamp < start_time):
                break

            if 'card' in x:
                card = json.loads(x["card"])
                if 'item' in card:
                    flag = False
                    if 'description' in card["item"]:
                        text = card["item"]["description"]
                    elif 'content' in card["item"]:
                        text = card["item"]["content"]
                    else:
                        text = None
                    if text:
                        for keyword in task_config["keywords"]:
                            if keyword in text:
                                uname = x["desc"]["user_profile"]["info"]["uname"]  #动态的主人的用户名
                                dyid = x["desc"]["dynamic_id"]
                                if dyid in already_repost_dyid: #若动态被转发过就跳过
                                    continue
                                
                                if isinstance(task_config["repost"], list):
                                    if len(task_config["repost"]) > 0:
                                        repost: str = task_config["repost"][randint(0, len(task_config["repost"]) - 1)] #取随机评论
                                    else:
                                        repost: str = ''
                                else:
                                    repost: str = task_config["repost"]

                                if isinstance(task_config["reply"], list):
                                    if len(task_config["reply"]) > 0:
                                        reply: str = task_config["reply"][randint(0, len(task_config["reply"]) - 1)]
                                    else:
                                        reply: str = ''
                                else:
                                    reply: str = task_config["reply"]

                                try:
                                    await biliapi.dynamicRepostReply(dyid, repost)
                                    detail = await biliapi.getDynamicDetail(dyid)
                                    oid = detail["data"]["card"]["desc"]["rid"]
                                    await biliapi.dynamicReplyAdd(oid, reply)
                                    logging.info(f'{biliapi.name}: 转发评论关键字动态(用户名:{uname},动态id:{dyid})成功')
                                except Exception as e: 
                                    logging.warning(f'{biliapi.name}: 转发评论关键字动态(用户名:{uname},动态id:{dyid})异常，原因为{str(e)}')
                                flag = True
                                break
                    if flag:
                        await asyncio.sleep(3)
                        continue

            if 'extension' in x and 'lott' in x["extension"]: #若抽奖标签存在
                uname = x["desc"]["user_profile"]["info"]["uname"]  #动态的主人的用户名
                dyid = x["desc"]["dynamic_id"]
                if dyid in already_repost_dyid: #若动态被转发过就跳过
                    continue

                if isinstance(task_config["repost"], list):
                    if len(task_config["repost"]) > 0:
                        repost: str = task_config["repost"][randint(0, len(task_config["repost"]) - 1)] #取随机评论
                    else:
                        repost: str = ''
                else:
                    repost: str = task_config["repost"]

                if isinstance(task_config["reply"], list):
                    if len(task_config["reply"]) > 0:
                        reply: str = task_config["reply"][randint(0, len(task_config["reply"]) - 1)]
                    else:
                        reply: str = ''
                else:
                    reply: str = task_config["reply"]

                try:
                    await biliapi.dynamicRepostReply(dyid, repost) #这里转发到自己的动态
                    detail = await biliapi.getDynamicDetail(dyid)
                    oid = detail["data"]["card"]["desc"]["rid"]
                    await biliapi.dynamicReplyAdd(oid, reply)    #这里评论
                    logging.info(f'{biliapi.name}: 转发评论抽奖动态(用户名:{uname},动态id:{dyid})成功')
                except Exception as e: 
                    logging.warning(f'{biliapi.name}: 转发评论抽奖动态(用户名:{uname},动态id:{dyid})异常，原因为{str(e)}')
                await asyncio.sleep(3)

    except Exception as e: 
        logging.warning(f'{biliapi.name}: 获取动态列表、异常，原因为{str(e)}，跳过转发抽奖动态')
        return
