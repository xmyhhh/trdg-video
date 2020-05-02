import os
import random as rnd
import  cv2
from PIL import Image, ImageFilter
from trdg import computer_text_generator, background_generator, distorsion_generator
try:
    from trdg import handwritten_text_generator
except ImportError as e:
    print("Missing modules for handwritten text generation.")
class FakeTextDataGenerator(object):
    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """
        cls.generate(*t)
    @classmethod
    def generate(
        cls,
        index,
        text,
        font,
        out_dir,
        size,
        extension,
        skewing_angle,
        random_skew,
        blur,
        random_blur,
        background_type,
        distorsion_type,
        distorsion_orientation,
        is_handwritten,
        name_format,
        width,
        alignment,
        text_color,
        orientation,
        space_width,
        character_spacing,
        margins,
        fit,
        output_mask,
        word_split,
        image_dir,
        font_size,
        string_num,
        close_string_num,
        font_size_min
    ):
        text_imageList=[]
        text_maskList=[]
        stringList=[]
        string=''
        words=text.split('\n')
        del words[len(words)-1]
        ave_length=int(len(words)/string_num)
        for j in range(string_num):
            for i in range(ave_length):
                string+=words[i+j*ave_length]
            stringList.append(string)
            string=''
        ##########################
        # Create picture of text and backgroundImg #
        ##########################
        background_img = background_generator.image(image_dir)
        for i in range(string_num):
            if font_size_min==-1:
                if font_size == -1 :#auto
                    text_image, text_mask = computer_text_generator.generate(
                        stringList[i],
                        font,
                        text_color,
                        int(background_img.size[1]/16),
                        orientation,
                        space_width,
                        character_spacing,
                        fit,
                        word_split,
                    )
                    text_imageList.append(text_image)
                    text_maskList.append(text_mask)
                else : #const
                    text_image, text_mask = computer_text_generator.generate(
                        stringList[i],
                        font,
                        text_color,
                        font_size,
                        orientation,
                        space_width,
                        character_spacing,
                        fit,
                        word_split,
                    )
                    text_imageList.append(text_image)
                    text_maskList.append(text_mask)
            else :#random
                import random
                text_image, text_mask = computer_text_generator.generate(
                    stringList[i],
                    font,
                    text_color,
                    random.randint(font_size_min,font_size),
                    orientation,
                    space_width,
                    character_spacing,
                    fit,
                    word_split,
                )
                text_imageList.append(text_image)
                text_maskList.append(text_mask)
        #############################
        # Place text with alignment #
        #############################
        def getPoint(background_img,text_image):
            import random
            x = random.randint(0, background_img.size[0] - text_image.size[0])
            y = random.randint(0, background_img.size[1] - text_image.size[1])
            return x,y
        def getClosePoint(background_img, text_image,stringAreaDict,arrangement):
            import random
            if arrangement==0: #horizontal
                x = random.randint(stringAreaDict["point_up_left"][0]-text_image.size[0], stringAreaDict["point_down_right"][0])
                if random.randint(0,1)==0:#up
                    y = stringAreaDict["point_up_left"][1]-text_image.size[1]
                else :  #down
                    y = stringAreaDict["point_down_right"][1]
            else : #Vertical
                y = random.randint(stringAreaDict["point_up_left"][1] - text_image.size[1],
                                   stringAreaDict["point_down_right"][1])
                if random.randint(0, 1) == 0:  # left
                    x = stringAreaDict["point_up_left"][0] - text_image.size[0]
                else:  # right
                    x = stringAreaDict["point_down_right"][0]

            return x, y
        def isCross(x0,y0,text_image,stringArea):
            for i in range(4):
                if i==0:
                    x=x0+text_image.size[0]
                    y=y0+text_image.size[1]
                elif i==1:
                    x=x0
                    y=y0+text_image.size[1]
                elif i==2:
                    x=x0+text_image.size[2]
                    y=y0
                else:
                    x=x0
                    y=y0
                for Area in stringArea:
                    if((Area["point_up_left"][0]<x and Area["point_up_left"][1]<y and Area["point_down_right"][0]>x and Area["point_down_right"][1]>y)):
                        return True
                return  False
        def alignment(background_img,text_imageList,image_dir):
            stringArea=[]
            for text_image  in text_imageList:
                while(background_img.size[0] < text_image.size[0] or background_img.size[1] < text_image.size[1]):
                    background_img = background_generator.image(image_dir)#change a big back pic
            head_stringAreaDict={}
            for idx, text_image in enumerate(text_imageList):
                if close_string_num==1:#string area non-relate
                    x0, y0 =getPoint(background_img,text_image)
                    while(isCross(x0,y0,text_image,stringArea)):
                        x0,y0=getPoint(background_img,text_image)
                    background_img.paste(text_image, (x0, y0), text_image)
                    AreaDict= {}
                    AreaDict['text']=stringList[idx]
                    AreaDict['point_up_left']=[x0,y0]
                    AreaDict['point_down_right']=[x0+text_image.size[0],y0+text_image.size[1]]
                    stringArea.append(AreaDict)
                elif (idx+1) % close_string_num==1 :#head of close string
                    x0, y0 = getPoint(background_img, text_image)
                    while (isCross(x0, y0, text_image, stringArea)):
                        x0, y0 = getPoint(background_img, text_image)
                    background_img.paste(text_image, (x0, y0), text_image)
                    AreaDict = {}
                    AreaDict['text'] = stringList[idx]
                    AreaDict['point_up_left'] = [x0, y0]
                    AreaDict['point_down_right'] = [x0 + text_image.size[0], y0 + text_image.size[1]]
                    stringArea.append(AreaDict)
                    head_stringAreaDict=AreaDict
                else :
                    x0, y0 = getClosePoint(background_img, text_image,head_stringAreaDict,1)
                    while (isCross(x0, y0, text_image, stringArea)):
                        x0, y0 = getClosePoint(background_img, text_image,head_stringAreaDict,1)
                    background_img.paste(text_image, (x0, y0), text_image)
                    AreaDict = {}
                    AreaDict['text'] = stringList[idx]
                    AreaDict['point_up_left'] = [x0, y0]
                    AreaDict['point_down_right'] = [x0 + text_image.size[0], y0 + text_image.size[1]]
                    stringArea.append(AreaDict)
                    head_stringAreaDict["point_up_left"][0] = min(AreaDict["point_up_left"][0],
                                                                  head_stringAreaDict["point_up_left"][0])
                    head_stringAreaDict["point_up_left"][1] = min(AreaDict["point_up_left"][1],
                                                                  head_stringAreaDict["point_up_left"][1])
                    head_stringAreaDict["point_down_right"][0] = max(AreaDict["point_down_right"][0],
                                                                  head_stringAreaDict["point_down_right"][0])
                    head_stringAreaDict["point_down_right"][1] = max(AreaDict["point_down_right"][1],
                                                                  head_stringAreaDict["point_down_right"][1])
            return background_img,stringArea
        final_image,stringArea =alignment(background_img,text_imageList,image_dir)
        #####################################
        # Generate name for resulting image #
        #####################################
        if name_format == 0:
            image_name = "{}.{}".format(str(index), extension)
        elif name_format == 1:
            image_name = "{}_{}.{}".format(str(index), text, extension)
        elif name_format == 2:
            image_name = "{}.{}".format(str(index), extension)
        else:
            print("{} is not a valid name format. Using default.".format(name_format))
            image_name = "{}_{}.{}".format(text, str(index), extension)

        # Save the image
        if out_dir is not None:
            final_image.convert("RGB").save(os.path.join(out_dir, image_name))
        else:
            return final_image.convert("RGB")
         #save gt
        import utils
        gt={}
        annotations={}
        for idx,Area in enumerate(stringArea):
            annotations[str(idx)]=Area
        gt['img_name']=image_name
        gt['annotations']=annotations
        import json
        utils.file_create("out/"+image_name.replace(extension,"json"),json.dumps(gt))

