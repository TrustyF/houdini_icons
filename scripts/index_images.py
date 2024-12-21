import os
import glob
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from icon_model import Base
from PIL import Image
import base64
import json

vips_home = r'C:\vips-dev-8.16\bin'
os.environ['PATH'] = vips_home + ';' + os.environ['PATH']
import pyvips

load_dotenv()
main_dir = os.path.dirname(os.path.abspath(__file__))
svg_files = glob.glob(os.path.join(main_dir, '**', '*.svg'), recursive=True)

engine = create_engine("sqlite:///icon_db.db")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

client = OpenAI(api_key=os.getenv("open_ai_key"))


def encode_image(image_path):
    conv_image = pyvips.Image.new_from_file(image_path, dpi=300)
    buffer = conv_image.write_to_buffer('.jpg')
    img_string = base64.b64encode(buffer).decode('utf-8')

    # with open('test2.jpg','wb') as fw:
    #     fw.write(base64.b64decode(img_string))

    return img_string


base64_image = encode_image(svg_files[0])

# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     response_format={"type": "json_object"},
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "could you give me a json with tags that represent the contents of this image ?"},
#                 {
#                     "type": "image_url",
#                     "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
#                 },
#             ]
#         }
#     ]
# )
#
# content = response.choices[0].message.content

# with open('temp_resp.json', 'w') as outfile:
#     json.dump(json.loads(content), outfile, indent=1)

with open('temp_resp.json', 'r') as infile:
    tags = json.load(infile)
