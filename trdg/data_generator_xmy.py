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
        margins,
        fit,
        output_mask,
        word_split,
        image_dir,
        load_dict
    ):
        text_imageList=[]
        text_maskList=[]
        stringList=[]
        string=''
        words=text.split('\n')
        del words[len(words)-1]

        ##########################
        # Create picture of text and backgroundImg #
        ##########################
        background_img = background_generator.image(image_dir)
       #西瓜视频

        for idx,stringFormat in enumerate(load_dict['stringFormats']):
            string = ''
            for j in range(stringFormat['length']):
                string += words[idx + j]
            text_image, text_mask = computer_text_generator.generate(
                string,
                font,
                stringFormat['text_color'],
                stringFormat['size'],
                stringFormat['orientation'],
                stringFormat['space_width'],
                stringFormat['character_spacing'],
                stringFormat['fit'],
                stringFormat['word_split'],
            )
            positon=stringFormat['position']
            #############################
            # Place text with alignment #
            #############################
            def alignment(background_img,text_image,x0,y0,image_dir):
                stringArea=[]
                for text_image  in text_imageList:
                    i = 0
                    while (background_img.size[0] < text_image.size[0] or background_img.size[1] < text_image.size[1]):
                        background_img = background_generator.image(image_dir)  # change a big back pic
                        i += 1
                        if i == 10:
                            return None, None
                background_img.paste(text_image, (x0, y0), text_image)
                AreaDict= {}
                AreaDict['text']="x"
                AreaDict['point_up_left']=[x0,y0]
                AreaDict['point_down_right']=[x0+text_image.size[0],y0+text_image.size[1]]
                stringArea.append(AreaDict)
                return background_img,stringArea
            final_image,stringArea =alignment(background_img,text_image,stringFormat['position']['x'],stringFormat['position']['y'],image_dir)
            background_img=final_image
        #####################################
        # Generate name for resulting image #
        #####################################
        if final_image!=None:
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
        else:
            print("None img")