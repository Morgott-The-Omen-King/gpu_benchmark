#!/usr/bin/env python3
import os
import shutil
import json
from pathlib import Path

# 定义路径
script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
source_dir = os.path.join(script_dir, "MOSE")  # 已存在的MOSE目录
# 获取源视频ID
train_source_dir = os.path.join(source_dir, "train")
valid_source_dir = os.path.join(source_dir, "valid")

# 获取列表文件路径
train_list_file = "training/assets/MOSE_sample_train_list.txt"
val_list_file = "training/assets/MOSE_sample_val_list.txt"

# 读取视频ID列表
def read_video_ids(list_file):
    with open(list_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# 查找源目录中已存在的视频ID
def find_source_video_id(source_type_dir):
    jpeg_dir = os.path.join(source_type_dir, "JPEGImages")
    if os.path.exists(jpeg_dir):
        subdirs = [d for d in os.listdir(jpeg_dir) if os.path.isdir(os.path.join(jpeg_dir, d))]
        if subdirs:
            return subdirs[0]  # 返回第一个找到的视频ID
    return None

# 复制视频文件并重命名为新的视频ID
def copy_and_rename(source_type_dir, source_video_id, target_video_id):
    # JPEGImages复制
    source_frames = os.path.join(source_type_dir, "JPEGImages", source_video_id)
    target_frames = os.path.join(source_type_dir, "JPEGImages", target_video_id)
    
    # Annotations复制
    source_annos = os.path.join(source_type_dir, "Annotations", source_video_id)
    target_annos = os.path.join(source_type_dir, "Annotations", target_video_id)
    
    if not os.path.exists(source_frames) or not os.path.exists(source_annos):
        print(f"警告: 源视频或标注目录不存在: {source_frames} 或 {source_annos}")
        return False
    
    # 创建目标目录
    os.makedirs(target_frames, exist_ok=True)
    os.makedirs(target_annos, exist_ok=True)
    
    # 复制JPEGImages
    for file in os.listdir(source_frames):
        if file.endswith('.jpg'):
            shutil.copy(os.path.join(source_frames, file), os.path.join(target_frames, file))
    
    # 复制Annotations
    for file in os.listdir(source_annos):
        if file.endswith('.png'):
            shutil.copy(os.path.join(source_annos, file), os.path.join(target_annos, file))
    
    print(f"已复制视频: {target_video_id}")
    return True

# 更新元数据JSON文件
def update_metadata_json(dir_type, video_ids):
    json_path = os.path.join(source_dir, dir_type, f"meta_{dir_type}.json")
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                meta_data = json.load(f)
            
            source_video_id = None
            for vid in meta_data.get("videos", {}):
                source_video_id = vid
                break
            
            if not source_video_id:
                print(f"警告: 在{json_path}中未找到源视频ID")
                return
            
            source_meta = meta_data["videos"][source_video_id]
            
            # 为每个目标视频ID添加相同的元数据
            for video_id in video_ids:
                if video_id != source_video_id and video_id not in meta_data["videos"]:
                    meta_data["videos"][video_id] = source_meta.copy()
            
            # 保存更新后的JSON
            with open(json_path, 'w') as f:
                json.dump(meta_data, f, indent=2)
            
            print(f"已更新元数据文件: {json_path}")
        except Exception as e:
            print(f"处理JSON文件时出错: {e}")
    else:
        print(f"警告: 未找到元数据文件 {json_path}")

def main():
    # 获取源视频ID
    train_source_id = find_source_video_id(train_source_dir)
    valid_source_id = find_source_video_id(valid_source_dir)
    
    if not train_source_id or not valid_source_id:
        print("错误: 未找到源视频ID，请确保MOSE目录中已包含视频数据")
        return
    
    print(f"找到训练集源视频ID: {train_source_id}")
    print(f"找到验证集源视频ID: {valid_source_id}")
    
    # 读取需要创建的视频ID列表
    train_video_ids = read_video_ids(train_list_file)
    val_video_ids = read_video_ids(val_list_file)
    
    print(f"从训练集列表中读取了 {len(train_video_ids)} 个视频ID")
    print(f"从验证集列表中读取了 {len(val_video_ids)} 个视频ID")
    
    # 复制训练集视频
    train_success_count = 0
    for video_id in train_video_ids:
        # 跳过源视频ID
        if video_id == train_source_id:
            print(f"跳过源训练视频ID: {video_id}")
            train_success_count += 1
            continue
            
        if copy_and_rename(train_source_dir, train_source_id, video_id):
            train_success_count += 1
    
    # 复制验证集视频
    val_success_count = 0
    for video_id in val_video_ids:
        # 跳过源视频ID
        if video_id == valid_source_id:
            print(f"跳过源验证视频ID: {video_id}")
            val_success_count += 1
            continue
            
        if copy_and_rename(valid_source_dir, valid_source_id, video_id):
            val_success_count += 1
    
    print(f"成功复制 {train_success_count}/{len(train_video_ids)} 个训练视频")
    print(f"成功复制 {val_success_count}/{len(val_video_ids)} 个验证视频")
    
    # 更新元数据文件
    update_metadata_json("train", train_video_ids)
    update_metadata_json("valid", val_video_ids)
    
    print("复制完成！")

if __name__ == "__main__":
    main() 