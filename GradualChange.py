# -*- coding = utf-8 -*-
import numpy as np
from pkg_resources import resource_stream
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw

pixels = "#$@&%ZYXWVUTSRQPONMLKJIHGFEDCBA0987654321zyxwvutsrqponmlkjihgfedcba?][}{/)(><*+-."

def main():
    toChars(video_path=r"D:\projects\Python\VideoToChars\Test\【名场面】糟糕的姿势！动漫里那些万恶之源名场面盘点！.flv",
            chars_width=30,     # 最低字符分辨率
            gradual=80,         # 最高字符分辨率
            t_start=40,
            t_end=53)

def toChars(video_path, chars_width, gradual, t_start, t_end):
    chars = VideoToChars(video_path=video_path, chars_width=chars_width,
                         gradual=gradual, t_start=t_start, t_end=t_end)
    CharsVideo = chars.saveVideo()
    CharsVideo.write_videofile(r"Test/2_4.mp4")

class VideoToChars:
    def __init__(self, video_path, chars_width, gradual, t_start=0, t_end=None):
        # 读取原视频要处理的部分
        self.old_video_clip = VideoFileClip(video_path).subclip(t_start, t_end)

        # 字符串
        self.pixels = pixels

        # 读取的帧数
        self.fps = self.old_video_clip.fps

        # 获取字符大小处理
        font_fp = resource_stream("video01", "字体.ttf")
        self.font = ImageFont.truetype(font_fp, size=14)  # 使用等宽字体
        self.font_width = sum(self.font.getsize("a")) // 2  # 为了保证像素宽高一致，均取宽高的平均值

        '''
        # 渐变字符分辨率处理
        '''
        # 记录渐变级别(gradual),初始化渐变级别计数(g_count),渐变级别帧数单位（perL）
        self.gradual = gradual
        self.fps_count = 0
        self.g_count = 0
        # 每个级别帧数
        self.perL = int(self.old_video_clip.fps * self.old_video_clip.duration / (self.gradual - chars_width))
        print(self.perL)

        # 字符分辨率处理
        self.chars_width = int(chars_width)
        self.chars_height = int(chars_width / self.old_video_clip.aspect_ratio)
        # 新视频固定长宽
        self.gradual_width = int(gradual)
        self.gradual_height = int(gradual / self.old_video_clip.aspect_ratio)
        self.newVideo_width = int(self.gradual_width * self.font_width), int(self.gradual_height * self.font_width)
        # 重置旧视频长宽赋给新视频
        # self.new_video_clip: VideoClip = self.old_video_clip.resize(self.newVideo_width)
        self.new_video_clip: VideoClip = self.old_video_clip.resize((self.gradual_width, self.gradual_height))

        # 渐变图像长宽处理
        self.g_char_width = []
        self.g_char_height = []
        self.g_video_size = []
        widthcount = self.chars_width
        for i in range(0, gradual - self.chars_width):
            width = int(widthcount)
            height = int(self.chars_height/self.chars_width * width)
            size = (width * self.font_width, height * self.font_width)
            self.g_video_size.append(size)
            self.g_char_width.append(width)
            self.g_char_height.append(height)
            widthcount += 1

    # 通过灰度图返回字符
    def getGray(self, gray):
        percent = gray / 255
        index = int(percent*(len(pixels)-1))
        return pixels[index]

    # 通过获得帧图像进行处理
    def getImage(self, t):
        # 获取到图像
        # new_video_clip: VideoClip = self.old_video_clip.resize((self.g_char_width[self.g_count],
        #                                                         self.g_char_height[self.g_count]))
        # img_np = new_video_clip.get_frame(t)  # 获取帧图像
        img_np = self.new_video_clip.get_frame(t)  # 获取帧图像
        img1 = Image.fromarray(img_np, "RGB")  # 获取帧图像RGB数值
        img = img1.resize((self.g_char_width[self.g_count],
                          self.g_char_height[self.g_count]),
                          Image.NEAREST)
        img1.close()
        img_gray = img.convert(mode="L")  # 将图片转为灰度图
        img_chars = Image.new("RGB", (self.g_video_size[self.g_count]), color="darkgray")  # 新建白画布
        brush = ImageDraw.Draw(img_chars)  # 画笔
        for y in range(self.g_char_height[self.g_count]):
            for x in range(self.g_char_width[self.g_count]):
                px = img.load()     # 读取图像矩阵
                r, g, b = px[x, y]  # 获取图块颜色
                gray = img_gray.getpixel((x, y))  # 获取该图开灰度值
                char = self.getGray(gray)  # 通过灰度值获取字符

                position = x * self.font_width, y * self.font_width  # 获取x 横坐标，y纵坐标（向下为正）
                brush.text(position, char, fill=(r, g, b))  # 指定位置写入字符写入颜色
        img_chars1 = img_chars.resize(self.newVideo_width, Image.NEAREST)
        img_chars.close()
        self.fps_count += 1
        if self.fps_count > self.g_count * self.perL and self.g_count < self.gradual-self.chars_width - 1:
            self.g_count += 1
        return np.array(img_chars1)

    # 保存处理后的video
    def saveVideo(self):
        clip = VideoClip(self.getImage, duration=self.old_video_clip.duration)  # 处理图像

        return (clip.set_fps(self.fps)
                .set_audio(self.new_video_clip.audio))

if __name__ == "__main__":
    main()