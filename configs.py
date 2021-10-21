import requests
import numpy as np
import os, datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pytesseract


#pytesseract.pytesseract.tesseract_cmd = r""


BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

Bot = Client(
    "Bot",
    bot_token = BOT_TOKEN,
    api_id = API_ID,
    api_hash = API_HASH
)

START_TXT = """
Hi {}
I am subtitle extractor Bot.
> `I can extract hard-coded subtitle from videos.`
Send me a video to get started.
"""

START_BTN = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Source Code', url='https://github.com/samadii/VidSubExtract-Bot'),
        ]]
    )


@Bot.on_message(filters.command(["start"]))
async def start(bot, update):
    text = START_TXT.format(update.from_user.mention)
    reply_markup = START_BTN
    await update.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


#language
LANG='fas'
tessdata = f"https://github.com/tesseract-ocr/tessdata/raw/main/{LANG}.traineddata"
dirs = '/app/vendor/tessdata/'
path = f'{dirs}{LANG}.traineddata'
if not os.path.exists(path):
    data = requests.get(tessdata, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
    if data.status_code == 200:
        open(path, 'wb').write(data.content)
    else:
        print("Either the lang code is wrong or the lang is not supported.")


@Bot.on_message(filters.private & filters.video)
async def main(bot, m):
    videopath = "temp/thevideo.mp4"
    await m.download(videopath)
    sub_count = 0
    s = 0
    e = m.video.duration
    step = 0.1
    intervals = [round(num, 2) for num in np.linspace(s,e,(e-s)*int(1/step)+1).tolist()]
    for interval in intervals:
        os.system("ffmpeg -ss {interval} -i {videopath} -vframes 1 -q:v 2 -y temp/output.jpg")
        im = Image.open("temp/output.jpg")
        try:
            text = pytesseract.image_to_string(im, LANG)
        except:
            text = None
            pass
        if text is not None:
            sub_count += 1
            s_count = str(sub_count)
            from_time = str(datetime.datetime.fromtimestamp(interval)+datetime.timedelta(hours=0)).split(' ')[1][:12] + ' --> '
            to_time = str(datetime.datetime.fromtimestamp(interval+0.1)+datetime.timedelta(hours=0)).split(' ')[1][:12]
            with open('temp/srt.srt', 'a+') as f:
	        f.write("yh")  #s_count + '\n' + from_time + to_time + '\n' + text + '\n')
    f.close
    await m.reply_document(document="temp/srt.srt" ,caption=m.video.file_name)



Bot.run()
