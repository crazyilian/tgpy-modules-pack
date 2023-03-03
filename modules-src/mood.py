"""
    description: get most positive and negative messages in chat & get mood of one message
    name: mood
    version: 0.0.0
"""
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from datetime import datetime
from operator import itemgetter

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)


async def predict_and_get_top_results(ids, texts, title, msg):
    results = model.predict(texts, k=2)
    dict_pos = {}
    dict_neg = {}
    for id, res in zip(ids, results):
        if 'positive' in res:
            dict_pos[id] = res['positive']
        if 'negative' in res:
            dict_neg[id] = res['negative']
    if msg.chat:
        txt = f'TOP positive messages ' + title + ':'
        cnt = 0
        for id, val in reversed(sorted(dict_pos.items(), key=itemgetter(1))):
            txt = txt + f'\nlink: t.me/c/{msg.chat.id}/{id}\nval: {val}'
            cnt = cnt + 1
            if cnt >= 5:
                break
        await msg.reply(txt)
        txt = f'TOP negative messages ' + title + ':'
        cnt = 0
        for id, val in reversed(sorted(dict_neg.items(), key=itemgetter(1))):
            txt = txt + f'\nlink: t.me/c/{msg.chat.id}/{id}\nval: {val}'
            cnt = cnt + 1
            if cnt >= 5:
                break
        await msg.reply(txt)
    else:
        cnt = 0
        for id, val in reversed(sorted(dict_pos.items(), key=itemgetter(1))):
            await msg.respond(f'positive: {val}', reply_to=id)
            cnt = cnt + 1
            if cnt >= 5:
                break
        cnt = 0
        for id, val in reversed(sorted(dict_neg.items(), key=itemgetter(1))):
            await msg.respond(f'negative: {val}', reply_to=id)
            cnt = cnt + 1
            if cnt >= 5:
                break


async def topmoodcnt(topcnt_=1000):
    msg = ctx.msg
    ct = datetime.now().astimezone()
    texts = []
    ids = []
    topcnt = 0
    async for mess in client.iter_messages(msg.chat_id):
        if topcnt + 1 > topcnt_:
            break
        topcnt += 1
        try:
            if not isinstance(mess.text, str):
                continue
            if len(mess.text) < 10:
                continue
        except:
            continue
        texts.append(mess.text)
        ids.append(mess.id)
    await predict_and_get_top_results(ids, texts, f'among the last {topcnt}', msg)
    return 'Done'


async def topmood():
    msg = ctx.msg
    ct = datetime.now().astimezone()
    texts = []
    ids = []
    async for mess in client.iter_messages(msg.chat_id):
        if (ct - mess.date).days > 0:
            break
        try:
            if not isinstance(mess.text, str):
                continue
            if len(mess.text) < 10:
                continue
        except:
            continue
        texts.append(mess.text)
        ids.append(mess.id)
    await predict_and_get_top_results(ids, texts, 'of the day')
    return 'Done'


async def sentiment():
    msg = await ctx.msg.get_reply_message()
    txt = msg.text
    res = model.predict([txt])[0]
    return '\n' + '\n'.join(map(lambda el: f'{el[1]}: {round(el[0], 7)}',
                                filter(lambda el: el[0] > 0.0001, sorted(zip(res.values(), res.keys()), reverse=True))))


__all__ = ['sentiment', 'topmood', 'topmoodcnt']
