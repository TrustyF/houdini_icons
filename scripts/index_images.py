import os
import glob

from cffi.model import qualify
from dotenv import load_dotenv
from openai import OpenAI
from db_loader import session, Session_maker
from icon_model import Tag, Color, Shape, Icon, IconTagAssoc, IconShapeAssoc, IconColorAssoc, Symbol, \
    IconSymbolAssoc
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import base64
import json
import math

vips_home = r'C:\vips-dev-8.16\bin'
os.environ['PATH'] = vips_home + ';' + os.environ['PATH']
import pyvips

load_dotenv()
main_dir = os.path.dirname(os.path.abspath(__file__))
svg_files = glob.glob(os.path.join(main_dir, '**', '*.svg'), recursive=True)

client = OpenAI(api_key=os.getenv("open_ai_key"))


def encode_image(image_path, ico_name, ico_cat):
    conv_image = pyvips.Image.new_from_file(image_path, dpi=300)
    conv_image = pyvips.Image.thumbnail_image(conv_image, 100)

    sav_image = pyvips.Image.new_from_file(image_path, dpi=300)
    sav_image = pyvips.Image.thumbnail_image(sav_image, 200)
    Image.fromarray(sav_image.numpy()).save(
        f'C:/A_Mod/A_Projects/Webdev/houdini_icons/scripts/assets/converted_icons/{ico_cat}_{ico_name}.webp',
        "WebP", quality=100)

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
    # for path in svg_files[:2000]:
    #     make_icon(path)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(make_icon, path) for path in svg_files]
        results = [future.result() for future in futures]


def make_icon(icon_path):
    ico_name = os.path.splitext(os.path.basename(icon_path))[0]
    ico_category = os.path.basename(os.path.dirname(icon_path))
    ico_img = f'{ico_category}_{ico_name}.webp'

    if session.query(Icon).filter_by(image=ico_img).one_or_none():
        print(f"{ico_img} icon found, skipping")
        return

    # -----------------------------------------------------------
    print(ico_name)

    #  make image
    try:
        base64_image = encode_image(icon_path, ico_name, ico_category)
    except Exception:
        print(ico_name, " failed")
        return

    #  get attrib
    gen_attributes = make_ai_request(base64_image)

    # save to json
    with open(f'temp/{ico_name}.json', 'w') as outfile:
        json.dump(json.loads(gen_attributes), outfile, indent=1)

    #  read json
    try:
        with open(f'temp/{ico_name}.json', 'r') as infile:
            gen_attributes = json.load(infile)
    except:
        return

    local_session = Session_maker()

    # create icon
    icon = Icon(name=ico_name, category=ico_category, image=ico_img)
    local_session.add(icon)

    # make tags
    for tag in gen_attributes['tags']:
        t = local_session.query(Tag).filter_by(name=tag[0]).one_or_none()
        if not t:
            t = Tag(name=tag[0])

        assoc = IconTagAssoc(icon=icon, tag=t, weight=tag[1])
        local_session.add_all([t, assoc])
    # make shapes
    for shape in gen_attributes['shapes']:
        s = local_session.query(Shape).filter_by(name=shape[0]).one_or_none()
        if not s:
            s = Shape(name=shape[0])

        assoc = IconShapeAssoc(icon=icon, shape=s, weight=shape[1])
        local_session.add_all([s, assoc])
    # make symbols
    for symbol in gen_attributes['symbols']:
        sy = local_session.query(Symbol).filter_by(name=symbol[0]).one_or_none()
        if not sy:
            sy = Symbol(name=symbol[0])

        assoc = IconSymbolAssoc(icon=icon, symbol=sy, weight=symbol[1])
        local_session.add_all([sy, assoc])
    # make colors
    for color in gen_attributes['colors']:
        c = local_session.query(Color).filter_by(name=color[0]).one_or_none()
        if not c:
            c = Color(name=color[0])

        assoc = IconColorAssoc(icon=icon, color=c, weight=color[1])
        local_session.add_all([c, assoc])

    local_session.commit()
    local_session.close()


def dump_json():
    print('dumping json')
    all_icons = session.query(Icon).all()
    combined = []

    for ico in all_icons:
        dic = ico.to_dict()
        combined.append(dic)

    with open('C:/A_Mod/A_Projects/Webdev/houdini_icons/client/src/assets/database.json', 'w') as outfile:
        json.dump(combined, outfile, indent=1)


def remake_images():
    for i, icon_path in enumerate(svg_files):

        if i >= 50:
            break

        ico_name = os.path.splitext(os.path.basename(icon_path))[0]
        ico_category = os.path.basename(os.path.dirname(icon_path))
        ico_img = f'{ico_category}_{ico_name}.webp'
        #  make image
        try:
            base64_image = encode_image(icon_path, ico_name, ico_category)
        except Exception as e:
            print(ico_name, " failed", e)
            continue


def make_atlas():
    print('making atlas')
    output_path = "C:/A_Mod/A_Projects/Webdev/houdini_icons/client/public/atlas"

    for arr_index in range(100):

        total_ico = 100

        icons = (session.query(Icon.id, Icon.image, Icon.category).order_by(Icon.id)
                 .offset(arr_index * total_ico)
                 .limit(total_ico)
                 .all())

        if len(icons) < 1:
            print(f'finished at iter: {arr_index}')
            break

        print(arr_index,[x.id for x in icons])

        images = [Image.open(f'C:/A_Mod/A_Projects/Webdev/houdini_icons/scripts/assets/converted_icons/'
                             f'{icon.image}') for icon in icons]

        grid_size = (10, 10)
        cell_size = (100, 100)
        padding = 5

        cols, rows = grid_size
        cell_width, cell_height = cell_size
        atlas_width = cols * cell_width
        atlas_height = rows * cell_height

        # Create a blank atlas
        atlas = Image.new('RGBA', (atlas_width, atlas_height), (0, 0, 0, 0))  # Transparent background

        for idx, img in enumerate(images):

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
    # dump_json()
    make_atlas()
