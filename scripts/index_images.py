import os
import glob
import logging
from logging import Logger

from cffi.model import qualify
from dotenv import load_dotenv
from openai import OpenAI
from db_loader import session, Session_maker
from icon_model import Tag, Icon, IconTagAssoc
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import base64
import json
import math

vips_home = r'C:\vips-dev-8.16\bin'
os.environ['PATH'] = vips_home + ';' + os.environ['PATH']
import pyvips

log = logging.getLogger('custom')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

load_dotenv()
main_dir = os.path.dirname(os.path.abspath(__file__))
svg_files = glob.glob(os.path.join(main_dir, '**', '*.svg'), recursive=True)

client = OpenAI(api_key=os.getenv("open_ai_key"))


def encode_image(image_path, ico_name, ico_cat, i):
    conv_image = pyvips.Image.new_from_file(image_path, dpi=300, access="sequential")
    conv_image = pyvips.Image.thumbnail_image(conv_image, 100)

    # sav_image = pyvips.Image.new_from_file(image_path, dpi=300)
    # sav_image = pyvips.Image.thumbnail_image(sav_image, 200)
    # Image.fromarray(sav_image.numpy()).save(
    #     f'C:/A_Mod/A_Projects/Webdev/houdini_icons/scripts/assets/converted_icons/{i}_{ico_cat}_{ico_name}.webp',
    #     "WebP", quality=100)

    buffer = conv_image.write_to_buffer('.jpg')
    img_string = base64.b64encode(buffer).decode('utf-8')

    return img_string


def make_ai_request(img):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "could you give me a json with tags,shapes,symbols and colors that represent the "
                                "contents of this image ?"
                                " Tags should not contain things like: 'icon' or 'symbol'."
                                " Keep the shapes to simple primitives."
                                " The symbols should be simple single-word signs."
                                " At least 10 tags, max 3 shapes, max 3 symbols and max 3 colors."
                                " Also add a weight value for how relevant each is."
                                " it should be formated as [name,weight]."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"},
                    },
                ]
            }
        ]
    )

    return response.choices[0].message.content


def dispatch_icons():
    # for i,path in enumerate(svg_files):
    #     make_icon(i,path)

    print(f'all icons: {len(svg_files)}')

    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: make_icon(*args), enumerate(svg_files))


def make_icon(index, icon_path):
    index = index + 1

    def validate_name(name):
        return name.strip().lower().replace('_', '')

    ico_name = os.path.splitext(os.path.basename(icon_path))[0]
    ico_category = os.path.basename(os.path.dirname(icon_path))
    ico_img = f'{ico_category}_{ico_name}.webp'

    if session.query(Icon).filter_by(image=ico_img).one_or_none():
        # log.info(f'icon found skipping {ico_name}')
        return

    log.info(f'ico_name: {index}-{ico_name}')

    # check for dupe
    # matching_svg = glob.glob(os.path.join(main_dir, 'icons', '**', f'{ico_name}.svg'), recursive=True)
    # if len(matching_svg) > 1:

    # make image
    # try:
    #     base64_image = encode_image(icon_path, ico_name, ico_category, index)
    # except Exception as e:
    #     log.info(f'{ico_name} failed to make image. {e}')
    #     return
    #
    # log.info(f'requesting {ico_name}')
    #
    # #  get attrib
    # gen_attributes = make_ai_request(base64_image)
    #
    # # save to json
    # with open(f'temp_fixed_id/{index}_{ico_category}_{ico_name}.json', 'w') as outfile:
    #     json.dump(json.loads(gen_attributes), outfile, indent=1)

    #  read json
    try:
        with open(f'temp_fixed_id/{index}_{ico_category}_{ico_name}.json', 'r') as infile:
            gen_attributes = json.load(infile)
    except:
        log.info(f'{ico_name} json not found')
        return

    local_session = Session_maker()

    # create icon
    icon = Icon(id=index, name=ico_name, category=ico_category, image=ico_img)
    local_session.add(icon)

    # make tags
    for key, value in gen_attributes.items():

        for tag in value:
            name = validate_name(tag[0])
            t = local_session.query(Tag).filter_by(name=name).one_or_none()

            if not t:
                t = Tag(name=name, type=key[:-1])
                local_session.add(t)
                local_session.commit()

            if not session.query(IconTagAssoc).filter_by(icon_id=icon.id, tag_id=t.id).one_or_none():
                # make assoc
                assoc = IconTagAssoc(icon=icon, tag=t, weight=tag[1])
                local_session.add(assoc)
                local_session.commit()

    local_session.commit()
    local_session.close()


def dump_json():
    print('dumping json')
    all_icons = [x.to_dict() for x in session.query(Icon).all()]

    with open('C:/A_Mod/A_Projects/Webdev/houdini_icons/client/src/assets/database.json', 'w') as outfile:
        json.dump(all_icons, outfile)


def remake_images():
    for i, icon_path in enumerate(svg_files):

        index = i + 1

        ico_name = os.path.splitext(os.path.basename(icon_path))[0]
        ico_category = os.path.basename(os.path.dirname(icon_path))
        ico_img = f'{index}_{ico_category}_{ico_name}.webp'

        made = os.listdir(f'C:/A_Mod/A_Projects/Webdev/houdini_icons/scripts/assets/converted_icons')

        if ico_img in made:
            continue

        print(ico_img)

        #  make image
        try:
            base64_image = encode_image(icon_path, ico_name, ico_category,index)
        except Exception as e:
            print(ico_name, " failed", e)
            return


def make_atlas():
    print('making atlas')
    output_path = "C:/A_Mod/A_Projects/Webdev/houdini_icons/client/public/atlas"

    icons_paths = sorted(os.listdir(f'C:/A_Mod/A_Projects/Webdev/houdini_icons/scripts/assets/converted_icons'),
                         key=lambda x:int(x.split('_')[0]))
    # print(icons_paths)
    images = [Image.open(os.path.join('C:/A_Mod/A_Projects/Webdev/houdini_icons/scripts/assets/converted_icons', path))
              for path in icons_paths]

    chunk_images = [images[i:i + 100] for i in range(0, len(images), 100)]

    for (arr_index,img_arr) in enumerate(chunk_images):

        total_ico = 100
        grid_size = (10, 10)
        cell_size = (100, 100)
        padding = 5

        cols, rows = grid_size
        cell_width, cell_height = cell_size
        atlas_width = cols * cell_width
        atlas_height = rows * cell_height

        # Create a blank atlas
        atlas = Image.new('RGBA', (atlas_width, atlas_height), (0, 0, 0, 0))  # Transparent background

        for idx, img in enumerate(img_arr):

            if img.width != cell_width or img.height != cell_height:
                img.thumbnail((cell_size[0] - padding, cell_size[1] - padding))

            # Calculate grid position
            col = idx % cols
            row = idx // cols

            # Calculate paste position
            x_offset = (col * cell_width) + padding
            y_offset = (row * cell_height) + padding

            # Paste the image onto the atlas
            atlas.paste(img, (x_offset, y_offset))

        # Save the atlas
        atlas.save(output_path + f'/atlas_{arr_index}.webp', "WebP", quality=100)


if __name__ == '__main__':
    # dispatch_icons()
    dump_json()
    # make_atlas()
