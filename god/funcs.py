# AUTOGENERATED! DO NOT EDIT! File to edit: 01_core_fun.ipynb (unless otherwise specified).

__all__ = ['FindFilesByExtension', 'Lht_CreateTestDataset', 'lht_compose_transforms', 'lht_load_json',
           'randomSelectSamples', 'lht_generate_cocojson', 'lhtGenerateTestData', 'searchImageByName']

# Cell
import os
from torchvision import transforms
from god import LhtFile
import json
import numpy as np
import shutil

# Cell
def FindFilesByExtension(root_directory, extension):
    ret = []
    for (root, dirs, files) in os.walk(root_directory, topdown=True):
        for f in files:
            if f.endswith(extension):
                fileName = f
                filePath = os.path.join(root,f)
                lhtFile = LhtFile(fileName,filePath)
                ret.append(lhtFile)
    return ret
#

# Cell
def Lht_CreateTestDataset(matrix, xSize, ySize, step):
    '''
    generate slide windows
    Parameters:
        matrix: an image array, height X width X channel
        xSize: width of a slide window
        ySize: height of a slide window
        step : length of slide step.
    Returns:
        rtn: a list of dictionary objects
        {'data':d, 'bbox':bbox, 'category_id': -1}
    '''
    rtn = []
    rowNum = len(matrix)
    colNum = len(matrix[0])
    for i in range(0, colNum, step):
        for j in range(0, rowNum, step):
            bbox = [i,j,xSize,ySize]
            col,row,colSize, rowSize = bbox
            d = matrix[row:row+rowSize, col:col+colSize,:]
            a = {'data':d, 'bbox':bbox, 'category_id': -1}
            rtn.append(a)
    return rtn

# Cell
def lht_compose_transforms(size):
    '''
    create torch composed transform object. PILImage object -> resized object -> tensor object
    Parameter:
        size: sequence or int. something like [h,w]
    Return:
        rtn: torchvision.transforms.transforms.Compose object
    '''
    ret = transforms.Compose([transforms.ToPILImage(), transforms.Resize(size),  transforms.ToTensor()])
    return ret

# Cell
def lht_load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            obj = json.load(f)
        return obj
    except FileNotFoundError as err:
        print(err)
        return -1


# Cell
def randomSelectSamples(jsonList, num):
    '''
    randomly select 'num' images from each folder.
    Parameters:
        jsonList: a list of json files
        num: the number of you want
    Return:
        ret: a dictionary.
            - ['images', 'type', 'annotations', 'categories']
    '''
    ret = {}
    for js_id, js in enumerate(jsonList):
        try:
            obj_json = lht_load_json(js.file_path)
            if obj_json == -1:
                raise FileNotFoundError
            n = len(obj_json['images'])

            if n == 0:
                raise ValueError("No value!")
            #
            dirName = os.path.dirname(js.file_path)
            objs = np.random.choice(obj_json['images'], num, replace=False)
            obj_ids = [i['id'] for i in objs]
            for obj in objs:
                fp = dirName + "\\" + obj['file_name']
                obj['file_path'] = fp
            annotation = filter(lambda i: i['image_id'] in obj_ids, obj_json['annotations'])
            annotation = list(annotation)
            #
            d = {'images': objs.tolist(), 'annotations': annotation, 'categories':obj_json['categories']}
            ret[js_id] = d
            #
        except FileNotFoundError as err:
            continue
        except ValueError as err:
            continue
    return ret
#

# Cell
def lht_generate_cocojson(oldjson):
    images = []
    annotations = []
    category = [{'id':0,'category_name': "None"}, {'id':1,'category_name': "animal"}]
    #
    im_idx = 0
    bb_idx = 0
    for i in oldjson.values():
        for im in i['images']:
            im_id = im['id']
            im_ann = filter(lambda m: m['image_id']==im_id, i['annotations'])
            im_ann = list(im_ann)
            #
            im_newID = im_idx
            im['id'] = im_newID
            images.append(im)
            for an in im_ann:
                an['image_id'] = im_newID
                an['id'] = bb_idx
                an['category_id'] = 1
                bb_idx += 1
                annotations.append(an)
            #
            im_idx += 1
    #
    ret = {'images':images, 'annotations':annotations, 'categories': category}
    return ret
#

# Cell
def lhtGenerateTestData(source, destination, num):
    '''
    randomly copy n images from source folder to destination.
    Parameters:
        source: source directory path
        destination: destination path
        num: the number of images
    Return:
        ret_json: a json file that record the detail info of images
    '''
    target_dir = destination
    rd = source
    jsonList = FindFilesByExtension(rd,".json")
    ret_json = randomSelectSamples(jsonList,num)
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.mkdir(target_dir)
    for v in ret_json.values():
        for v_im in v['images']:
            shutil.copy(v_im['file_path'], target_dir)
            v_im.pop('file_path', None)
    #
    ret_coco = lht_generate_cocojson(ret_json)
    fp = target_dir + "\\" + "test.json"
    with open(fp, 'w') as fin:
        json.dump(ret_coco, fin)
    #
    return ret_coco

# Cell
def searchImageByName(image_name,js_dict):
    '''
    search images by its name, and return its index in a json file.
    Parameters:
        image_name: an image's name
        js_dict: a dictionary loaded from a json file, where save all details
    Return:
        a list where save the search results.
    '''
    images = js_dict['images']
    m = filter(lambda i: i['file_name'] == image_name, images)
    m = list(m)
    return m if len(m) >0 else -1
