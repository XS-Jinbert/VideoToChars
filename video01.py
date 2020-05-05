# -*- coding = utf-8 -*-
import numpy as np
from pkg_resources import resource_stream
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw

savepath = r"D:\projects\Python\VideoToChars\badapple"
videopath = r"D:\projects\Python\VideoToChars\badapple.mp4"
pixels = "#$@&%ZYXWVUTSRQPONMLKJIHGFEDCBA0987654321zyxwvutsrqponmlkjihgfedcba?][}{/)(><*+-."

def toChars(filename, chars_width, fps, pixels, output, t_start, t_end):
    video = VideotoChars(video_path=filename,
                         fps=fps,
                         chars_width=chars_width,
                         t_start=t_start,
                         t_end=t_end,
                         pixels=pixels)

    CharsVideo = video.outputVideo()
    CharsVideo.write_videofile(output)

class VideotoChars:
    def __init__(self, video_path, fps, pixels, chars_width, t_start=0, t_end=None):
        # 加载视频,并截取时间段
        video_clip = VideoFileClip(video_path).subclip(t_start, t_end)

        self.fps = fps

        # 像素形状，随意排
        self.pixels = pixels if pixels else \
            "#$@&%ZYXWVUTSRQPONMLKJIHGFEDCBA0987654321zyxwvutsrqponmlkjihgfedcba?][}{/)(><*+-."

        # 设置字符视频长宽字符数
        self.chars_width = chars_width
        self.chars_height = int(chars_width / video_clip.aspect_ratio)

        # 重置视频大小
        self.video_clip: VideoClip = video_clip.resize((self.chars_width, self.chars_height))

        # 字体相关
        font_fp = resource_stream("video01", "字体.ttf")
        self.font = ImageFont.truetype(font_fp, size=14)  # 使用等宽字体
        self.font_width = sum(self.font.getsize("a")) // 2  # 为了保证像素宽高一致，均取宽高的平均值

        # 重置视频的字符分辨率
        self.video_size = int(self.chars_width * self.font_width), int(self.chars_height * self.font_width)

    # 通过图块灰度返回字符
    def getGray(self, gray):
        percent = gray / 255  # 转换到 0-1 之间
        index = int(percent * (len(self.pixels) - 1))  # 拿到index
        return self.pixels[index]

    # 获取视频帧图片并转化为字符
    def getImage(self, t):
        # 获取到图像
        img_np = self.video_clip.get_frame(t)   # 获取帧图像
        img = Image.fromarray(img_np, "RGB")    # 获取帧图像RGB数值
        img_gray = img.convert(mode="L")        # 将图片转为灰度图

        img_chars = Image.new("RGB", self.video_size, color="white")  # 新建白画布
        brush = ImageDraw.Draw(img_chars)  # 画笔

        for y in range(self.chars_height):
            for x in range(self.chars_width):
                r, g, b = img_np[y][x]  # 获取图块颜色

                gray = img_gray.getpixel((x, y))  # 获取该图开灰度值
                char = self.getGray(gray)   # 通过灰度值获取字符

                position = x * self.font_width, y * self.font_width  # 获取x 横坐标，y纵坐标（向下为正）
                brush.text(position, char, fill=(r, g, b))  # 指定位置写入字符写入颜色
        return np.array(img_chars)

    def outputVideo(self):
        clip = VideoClip(self.getImage, duration=self.video_clip.duration)  # 处理图像

        return (clip.set_fps(self.fps)
                .set_audio(self.video_clip.audio))

if __name__ == '__main__':
    videopath = input("请输入文件路径和名字:")
    savepath = input("请输入保存路径和名字:")
    width = input("请输入视频字符分辨率:")
    start = input("请输入视频的开始时间(s):")
    end = input("请输入视频的截止时间(s):")
    toChars(filename=videopath, chars_width=int(width), fps=30, t_start=int(start), t_end=int(end), pixels=pixels, output=savepath)