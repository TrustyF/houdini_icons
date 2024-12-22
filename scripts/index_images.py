import os
import glob
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unicodedata import category

from icon_model import Base, Tag, Color, Shape, Icon
from PIL import Image
import base64
import json

vips_home = r'C:\vips-dev-8.16\bin'
os.environ['PATH'] = vips_home + ';' + os.environ['PATH']
import pyvips

load_dotenv()
main_dir = os.path.dirname(os.path.abspath(__file__))
svg_files = glob.glob(os.path.join(main_dir, '**', '*.svg'), recursive=True)

db_username = os.getenv('MYSQL_DATABASE_USERNAME')
db_password = os.getenv('MYSQL_DATABASE_PASSWORD')
db_name = 'TrustyFox$houdini_icons'

local_database_uri = f'mysql+pymysql://root:{db_password}@127.0.0.1:3306/{db_name}'
local_sqlite_uri = "sqlite:///assets/icon_db.db"

engine = create_engine(local_sqlite_uri)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

client = OpenAI(api_key=os.getenv("open_ai_key"))


def encode_image(image_path, ico_name, ico_cat):
    conv_image = pyvips.Image.new_from_file(image_path, dpi=300)
    buffer = conv_image.write_to_buffer('.jpg')
    img_string = base64.b64encode(buffer).decode('utf-8')

    Image.fromarray(conv_image.numpy()).save(f'output/converted_icons/{ico_cat}_{ico_name}.webp', "WebP", quality=50)

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
                        "text": "could you give me a json with tags,shapes and colors that represent the contents of "
                                "this image ? At least 10 tags, 3 shapes and 3 colors. Also add a weight value for how "
                                "relevant each is. it should be formated as [name,weight]"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"},
                    },
                ]
            }
        ]
    )

    return response.choices[0].message.content


def dump_json():
    all_icons = session.query(Icon).all()
    combined = []

    for ico in all_icons:
        dic = ico.to_dict()
        combined.append(dic)

    with open('output/database.json', 'w') as outfile:
        json.dump(combined, outfile, indent=1)


def make_icons():
    for l, icon_path in enumerate(svg_files):

        ico_name = os.path.splitext(os.path.basename(icon_path))[0]
        ico_category = os.path.basename(os.path.dirname(icon_path))

        base64_image = encode_image(icon_path, ico_name, ico_category)
        # gen_attributes = make_ai_request(base64_image)
        #
        # with open(f'temp/{ico_name}.json', 'w') as outfile:
        #     json.dump(json.loads(gen_attributes), outfile, indent=1)

        with open(f'temp/{ico_name}.json', 'r') as infile:
            gen_attributes = json.load(infile)

        if not session.query(Icon).filter_by(name=ico_name).one_or_none():
            icon = Icon(name=ico_name, category=ico_category, image=f'{ico_category}_{ico_name}.webp')

            for tag in gen_attributes['tags']:
                    t = session.query(Tag).filter_by(name=tag[0]).one_or_none()
                    if not t:
                        t = Tag(name=tag[0])
                    icon.tags.append(t)


            session.add(icon)
            print(icon)
        else:
            print(f"{ico_name} icon found, skipping")

        if l > 1:
            break

    # session.commit()
    # session.close()


if __name__ == '__main__':
    make_icons()
    dump_json()
