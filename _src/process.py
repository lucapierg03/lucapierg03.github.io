import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from imgs import IMGS
from PIL import Image, ImageChops
W='/tmp/claude-0/web'
OUT='/home/claude/lucapierg03.github.io/assets/img'
crops=[l.strip() for l in open(W+'/list.txt')]
old=[l.strip() for l in open(W+'/old/list.txt')]
Image.MAX_IMAGE_PIXELS=None
def load(src):
    if isinstance(src,int): return Image.open(W+'/'+crops[src])
    if src=='poster': return Image.open(W+'/'+crops[115]).rotate(-90, expand=True)
    if src.startswith('old:'): return Image.open(W+'/'+old[int(src[4:])])
    if src.startswith('/'): return Image.open(src)
    return Image.open(W+'/drive/'+src)
def flat(im):
    if im.mode in ('RGBA','LA','P'):
        im=im.convert('RGBA'); bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=im.split()[3]); return bg
    return im.convert('RGB')
def trim(im):
    bg=Image.new('RGB',im.size,(255,255,255))
    diff=ImageChops.difference(im,bg).convert('L').point(lambda p:255 if p>12 else 0)
    bb=diff.getbbox()
    if not bb: return im
    pad=int(0.03*max(bb[2]-bb[0],bb[3]-bb[1]))
    bb=(max(0,bb[0]-pad),max(0,bb[1]-pad),min(im.width,bb[2]+pad),min(im.height,bb[3]+pad))
    return im.crop(bb)
manifest={}
for slug,items in IMGS.items():
    os.makedirs(f'{OUT}/{slug}',exist_ok=True)
    lst=[]
    for n,(src,cap) in enumerate(items,1):
        im=trim(flat(load(src)))
        big=im.copy(); m=2600 if isinstance(src,str) and '/web/docs/' in src else 1800; big.thumbnail((m,m),Image.LANCZOS)
        sm=im.copy(); sm.thumbnail((760,760),Image.LANCZOS)
        big.save(f'{OUT}/{slug}/{n}.jpg',quality=84,optimize=True,progressive=True)
        sm.save(f'{OUT}/{slug}/{n}-sm.jpg',quality=80,optimize=True,progressive=True)
        lst.append({'src':f'{n}.jpg','sm':f'{n}-sm.jpg','w':big.width,'h':big.height,'sw':sm.width,'sh':sm.height,'cap':cap})
    manifest[slug]=lst
# headshot
os.makedirs(f'{OUT}/me',exist_ok=True)
h=Image.open(W+'/drive/headshot.jpg').convert('RGB')
h.thumbnail((700,900),Image.LANCZOS); h.save(f'{OUT}/me/luca.jpg',quality=85,optimize=True,progressive=True)
manifest['_me']={'w':h.width,'h':h.height}
json.dump(manifest,open(os.path.dirname(os.path.abspath(__file__))+'/manifest.json','w'),indent=1)
print('done')
