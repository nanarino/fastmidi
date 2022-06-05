"""谱面转midi核心工具

@author: 肝_败_吓_疯
"""

from decimal import Decimal, ROUND_HALF_UP
import re
import mido
from typing import Union
from io import BytesIO

dict_c = {"0": 0, "1": 60, "2": 62, "3": 64,
          "4": 65, "5": 67, "6": 69, "7": 71}

# 调号关系字典
key1 = {'c': 'C', 'c#': 'C#', 'd': 'D', 'd#': 'Eb', 'e': 'E', 'f': 'F', 'f#': 'F#', 'g': 'G',
        'g#': 'Ab', 'b': 'B', 'a#': 'Bb', 'a': 'A'}
# 各个调号相对于C调的音符偏移量字典
deta_dict = {'c': 0, 'c#': 1, 'd': 2, 'd#': 3, 'e': 4, 'f': 5, 'f#': 6, 'g': 7,
             'g#': 8, 'b': -1, 'a#': -2, 'a': -3}


def right_round(num: Union[int, float], keep_n: int):
    """精准的四舍五入方式 by 那个百分十先生 https://zhuanlan.zhihu.com/p/373694156"""
    if isinstance(num, float):
        num = str(num)
    return Decimal(num).quantize((Decimal('0.' + '0'*keep_n)), rounding=ROUND_HALF_UP)


def Q_FF(str1: str) -> bool:
    """定义过滤方法，过滤输入的调号变更信息"""
    return str1 != 'FF'


def main(d: str, nu: int, den: int, bpm: int, li: str):
    
    # 根据字典获取调号偏移量
    deta_diaohao = deta_dict.get(d.lower(), 0)

    # 转换BPM值为mido模块所需的时间值
    tempo = int(right_round(mido.bpm2tempo(bpm), 0))

    # 创建元数据信息
    meta_time = mido.MetaMessage('time_signature', numerator=nu, denominator=den)  # 节拍
    meta_tempo = mido.MetaMessage('set_tempo', tempo=tempo, time=0)  # BPM
    meta_tone = mido.MetaMessage('key_signature', key=key1[d.lower()])  # 调号

    # 创建声部，添加元数据信息
    mid = mido.MidiFile()  # 创建midi文件
    track = mido.MidiTrack()  # 建立一个音轨
    track2 = mido.MidiTrack()  # 建立第二个音轨
    mid.tracks.append(track)  # 添加音轨
    mid.tracks.append(track2)

    # 将元数据信息写入音轨中
    track.append(meta_time)
    track.append(meta_tempo)
    track.append(meta_tone)
    track2.append(meta_time)
    track2.append(meta_tempo)
    track2.append(meta_tone)

    # 定义正则表达式，找出文本中每个音符以及对应时长的字符串
    pattern = re.compile(r'\d\D*')
    # 执行正则
    li = pattern.findall(li)
    # 打印结果
    print("输入音符字符串为：", li[1:])

    def yuchuli(s: str):
        '''定义音符字符串解析函数，获取每个音符的音调、时长，转音关系、调号转换信息'''
        nonlocal deta_diaohao
        time = 480
        if s[0] != '9':
            yin_name = dict_c.get(s[0], 0)
        elif s[0] == '9':
            deta_diaohao = deta_dict.get(s[1:].lower(), 0)
            return 'FF'
        zt = 0
        up_half1 = 0
        if len(s) > 1 and s[0] != '9':
            if s[1] in {'q', 'w', 'e', 'r', 't', 'y', 'u'}:
                zt = -12
            elif '#' in s:
                up_half1 = 1
            elif s[1] in ['Q', 'W', 'E', 'R', 'T', 'Y', 'U']:
                zt = 12
            elif s[1] in ['a', 's', 'd', 'f', 'g', 'h', 'j']:
                zt = -24
            elif s[1] in ['A', 'S', 'D', 'F', 'G', 'H', 'J']:
                zt = 24
        if s[0] == '0':
            yin_name = 0
        else:
            yin_name = yin_name + zt + up_half1 + deta_diaohao
        for i in s:
            if i == '+':
                time += 480
            elif i == '=':
                time /= 4
            elif i == '-':
                time /= 2
            elif i == '_':
                time /= 8
            elif i == '.':
                time *= 1.5
        if '][' in s:
            a = 3
        elif ']' in s:
            a = 2
        elif '[' in s:
            a = 1
        else:
            a = 0
        return ([yin_name, int(time)], a)

    # map执行解析音符
    li2 = list(map(yuchuli, li))

    # 执行过滤，去除调号变更数据
    li2 = list(filter(Q_FF, li2))
    print("音符个数为：", len(li2))
    print("音符解析结果：", li2)

    def yin_append2(note_staus, note, time, countnum, tf):
        '''定义音符文件写入方法二，处理带有转音的音调'''
        if countnum % 2 != 0:
            if countnum == 1:
                num = 120
                num1 = 0
            elif tf == True:
                num = 120
                num1 = -120
            else:
                num = 0
                num1 = -120
            track.append(mido.Message(
                note_staus, note=note, velocity=96, time=0))
            track.append(mido.Message(
                'note_off', note=note, velocity=96, time=time+num))
            track2.append(mido.Message(
                'note_off', note=note, velocity=96, time=0))
            track2.append(mido.Message(
                'note_off', note=note, velocity=96, time=time+num1))
        else:
            if tf == True:
                num1 = 120
                num = -120
            else:
                num1 = 0
                num = -120
            track2.append(mido.Message(
                note_staus, note=note, velocity=96, time=0))
            track2.append(mido.Message(
                'note_off', note=note, velocity=96, time=time+num1))
            track.append(mido.Message(
                'note_off', note=note, velocity=96, time=0))
            track.append(mido.Message(
                'note_off', note=note, velocity=96, time=time+num))

    def yin_append1(note_staus, note, time):
        """定义音调写入文件方法一，处理无转音的音调"""
        track.append(mido.Message(
            note_staus,  note=note, velocity=96, time=0))
        track.append(mido.Message(
            'note_off', note=note, velocity=96, time=time))
        track2.append(mido.Message(
            'note_off', note=note, velocity=96, time=0))
        track2.append(mido.Message(
            'note_off', note=note, velocity=96, time=time))

    # 默认音符没有转音
    yin_group = False
    # 转音控制变量
    countnum = 1
    # 循环读取音符信息列表，写入mid文件
    for i in li2:
        if i[0][0] == 0:
            note_staus = 'note_off'
        else:
            note_staus = 'note_on'
        if i[1] == 0 and yin_group == False:
            yin_append1(note_staus, i[0][0], i[0][1])
        elif i[1] == 0 and yin_group == True:
            yin_append2(note_staus, i[0][0], i[0][1], countnum, yin_group)
            countnum += 1
        elif i[1] == 1:
            yin_group = True
            yin_append1(note_staus, i[0][0], i[0][1])
        elif i[1] == 2:
            yin_group = False
            yin_append2(note_staus, i[0][0], i[0][1], countnum, yin_group)
            countnum = 1
        elif i[1] == 3:
            yin_group = False
            yin_append2(note_staus, i[0][0], i[0][1], countnum, yin_group)
            yin_group = True
            countnum = 1

    # 保存文件
    output_buffer = BytesIO()
    mid.save(file = output_buffer)
    output_buffer.seek(0)
    return output_buffer


if __name__ == '__main__':
    pass