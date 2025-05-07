#!/usr/bin/env python
# Copyright (c) OpenMMLab. All rights reserved.

import os
import shutil
import json
import random
from pathlib import Path

def create_toy_coco_dataset(
    source_dir='~/yingkaining/dataset/coco',
    target_dir='data/coco',
    train_size=100,
    val_size=10
):
    """
    Create a toy COCO dataset with a subset of images.
    
    Args:
        source_dir (str): Source directory of the COCO dataset
        target_dir (str): Target directory to save the toy dataset
        train_size (int): Number of training images to include
        val_size (int): Number of validation images to include
    """
    # Expand user directory if needed
    source_dir = os.path.expanduser(source_dir)
    
    # Create target directories
    os.makedirs(os.path.join(target_dir, 'train2017'), exist_ok=True)
    os.makedirs(os.path.join(target_dir, 'val2017'), exist_ok=True)
    os.makedirs(os.path.join(target_dir, 'annotations'), exist_ok=True)
    
    # Process training set
    train_source_dir = os.path.join(source_dir, 'train2017')
    train_target_dir = os.path.join(target_dir, 'train2017')
    train_ann_file = os.path.join(source_dir, 'annotations', 'instances_train2017.json')
    train_target_ann_file = os.path.join(target_dir, 'annotations', 'instances_train2017.json')
    
    # Get all training images
    train_images = [f for f in os.listdir(train_source_dir) if f.endswith('.jpg')]
    # Randomly select subset
    selected_train_images = random.sample(train_images, min(train_size, len(train_images)))
    
    # Copy selected training images
    for img_file in selected_train_images:
        shutil.copy(
            os.path.join(train_source_dir, img_file),
            os.path.join(train_target_dir, img_file)
        )
    
    # Process validation set
    val_source_dir = os.path.join(source_dir, 'val2017')
    val_target_dir = os.path.join(target_dir, 'val2017')
    val_ann_file = os.path.join(source_dir, 'annotations', 'instances_val2017.json')
    val_target_ann_file = os.path.join(target_dir, 'annotations', 'instances_val2017.json')
    
    # Get all validation images
    val_images = [f for f in os.listdir(val_source_dir) if f.endswith('.jpg')]
    # Randomly select subset
    selected_val_images = random.sample(val_images, min(val_size, len(val_images)))
    
    # Copy selected validation images
    for img_file in selected_val_images:
        shutil.copy(
            os.path.join(val_source_dir, img_file),
            os.path.join(val_target_dir, img_file)
        )
    
    # Process annotations
    for split, ann_file, target_ann_file, selected_images in [
        ('train2017', train_ann_file, train_target_ann_file, selected_train_images),
        ('val2017', val_ann_file, val_target_ann_file, selected_val_images)
    ]:
        # Load original annotations
        with open(ann_file, 'r') as f:
            annotations = json.load(f)
        
        # Get image IDs for selected images
        selected_image_ids = set()
        for img_file in selected_images:
            img_id = int(os.path.splitext(img_file)[0])
            selected_image_ids.add(img_id)
        
        # Filter images
        filtered_images = [img for img in annotations['images'] 
                          if img['id'] in selected_image_ids]
        
        # Filter annotations
        filtered_annotations = [ann for ann in annotations['annotations'] 
                               if ann['image_id'] in selected_image_ids]
        
        # Create new annotation file
        new_annotations = {
            'info': annotations['info'],
            'licenses': annotations['licenses'],
            'images': filtered_images,
            'annotations': filtered_annotations,
            'categories': annotations['categories']
        }
        
        # Save new annotation file
        with open(target_ann_file, 'w') as f:
            json.dump(new_annotations, f)
    
    print(f"Toy COCO dataset created at {target_dir}")
    print(f"Training images: {len(selected_train_images)}")
    print(f"Validation images: {len(selected_val_images)}")

if __name__ == '__main__':
    create_toy_coco_dataset()
