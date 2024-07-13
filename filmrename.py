import os
import shutil
from datetime import datetime
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

def get_media_creation_date(file_path):
    ## 这部分是处理媒体的时间，图片的时间不能采用这一部分。
    try:
        # 创建解析器
        parser = createParser(file_path)
        # 提取元数据
        metadata = extractMetadata(parser)
        # 获取拍摄日期
        creation_date = metadata.get('creation_date')
        return creation_date

    except Exception as e:
        print(f"Error: {e}")
    # 如果无法获取拍摄日期，返回 None
    return None
def get_image_creation_time(image_path):
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 获取图片的 Exif 数据
            exif_data = img._getexif()

            # 如果存在 Exif 数据
            if exif_data is not None:
                # 解析 Exif 数据
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'DateTimeOriginal':
                        # 返回拍摄时间
                        return value

    except (AttributeError, KeyError, IndexError):
        pass

    # 如果无法获取拍摄时间，返回 None
    return None

def rename_photos_in_directory(directory_path):
    # 获取目录中的所有文件
    files = os.listdir(directory_path)
    DF = pd.DataFrame(columns = ['data_type',"num"])
    # files = ['2021:02:13 00:03:15ä¸å_0.jpeg']
    for file_name in files:
        # 拼接完整路径
        file_path = os.path.join(directory_path, file_name)
        ## 删除不需要的格式文件
        if '.heic' in file_name or '.DS_Store' in file_name :
            os.remove(file_path)
            print(f"remove {file_name}")
            continue
        print(file_name)
    # 检查是否为文件
        if os.path.isfile(file_path):
            # 获取文件创建时间
            created_time = os.path.getctime(file_path)
            if not file_path.split(".")[1] in ["MOV","mov","MP4","mp4"]:
                # 通过图片文件路径 来获取拍摄时间
                creation_time = get_image_creation_time(file_path)

                if creation_time is not None:
                    creation_time = datetime.strptime(creation_time.split(' ')[0], '%Y:%m:%d').strftime('%Y%m%d')
                    print(f"The photo was taken on: {creation_time}")
                else:
                    print("Unable to retrieve creation time.")
            else:
                # 视频文件路径 获取拍摄日期
                creation_time = get_media_creation_date(file_path)

                if creation_time is not None:
                    ##这里获取的时间就是datetime类型的，图片的是字符的。
                    creation_time = creation_time.strftime('%Y%m%d')
                    print(f"The media was created on: {creation_time}")
                else:
                    print("Unable to retrieve creation date.")

            # 转换为可读的时间格式
            formatted_time = datetime.fromtimestamp(created_time).strftime('%Y%m%d_%H%M%S').split("_")[0]
            file_type = file_name.split(".")[1]
            formatted_time = formatted_time if creation_time == None else creation_time
            data_type = formatted_time + '_' + file_type
            if data_type in list(DF['data_type']):
                # 构建新的文件名
                DF.loc[DF['data_type'] == data_type,'num'] += 1
                new_file_name = f"{formatted_time}_{DF.loc[DF['data_type']==data_type,'num'].values[0]}.{file_type}"
            else:
                new_file_name = f"{formatted_time}_0.{file_type}"
                DF = DF._append(pd.DataFrame({'data_type': [data_type], 'num': [0]}),ignore_index=True)

            # 如果目标文件夹不存在，则创建它
            new_folder = os.path.join(directory_path,new_file_name[:6])
            os.makedirs(new_folder, exist_ok=True)
            # 构建新的文件路径
            new_file_path = os.path.join(new_folder, new_file_name)

            # 重命名文件和移动文件的操作是一起的，所以执行的时候最好备份数据～
            shutil.move(file_path, new_file_path)
            print(f"Renamed: {file_name} to {new_file_name}")

# 指定包含照片的目录
directory_path = '//Users/carlos/photo/'

if __name__ == '__main__':
    # 调用函数进行批量重命名
    rename_photos_in_directory(directory_path)
