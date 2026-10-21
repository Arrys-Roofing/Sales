"""Browser stress test for Quick Price.
Run: pip install playwright && playwright install chromium && python tests/stress_test.py
Exits non-zero if any check fails."""
import sys
from playwright.sync_api import sync_playwright
import os
PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html')
html=open(PATH).read()
os.makedirs('test-output',exist_ok=True)
P=[]
def bug(m): P.append(m); print("BUG:",m)
with sync_playwright() as p:
    b=p.chromium.launch()
    def new(w=1200,touch=False):
        pg=b.new_page(viewport={'width':w,'height':900},has_touch=touch,is_mobile=touch)
        pg.errs=[]; pg.on('pageerror',lambda e: pg.errs.append(str(e)))
        pg.route('**/*fonts*',lambda r:r.abort()); pg.set_content(html); return pg
    pg=new()
    def ok(tag):
        hero=pg.text_content('#hPrice')
        pick=pg.query_selector('#ladder tr.pick td:nth-child(2)').text_content()
        if pick!=hero: bug(f'{tag}: pick {pick} != hero {hero}')
        if len(pg.query_selector_all('#ladder tr.click.cur'))>1: bug(f'{tag}: multiple highlighted')
        bt=pg.text_content('#build tr:last-child td:last-child')
        if bt!=hero: bug(f'{tag}: build-up total {bt} != hero {hero}')
        body=pg.inner_text('body')
        for t in ['NaN','Infinity','∞','undefined']:
            if t in body: bug(f'{tag}: {t} on page')
        if pg.is_visible('#errs'): bug(f'{tag}: error box showing unexpectedly')
    col=pg.eval_on_selector('#hPrice','e=>[getComputedStyle(e).color,getComputedStyle(e.parentElement).backgroundColor,getComputedStyle(e).backgroundColor]'); print('price colors',col)
    if col[2]!='rgba(0, 0, 0, 0)': bug('price still has its own background')
    ok('load')
    for k in ['me','ti','tp','sh']:
        pg.click(f'#types button[data-k="{k}"]'); ok('type '+k)
        if pg.query_selector('#presets button.on') is None or 'Target' not in pg.text_content('#presets button.on'): bug(f'type {k}: target preset not highlighted')
    for i in range(3):
        pg.click(f'#presets button >> nth={i}'); ok(f'preset {i}')
        if len(pg.query_selector_all('#presets button.on'))!=1: bug(f'preset {i} highlight')
    n=len(pg.query_selector_all('#ladder tr.click'))
    for i in range(n):
        before=pg.eval_on_selector_all('#ladder tr.click','r=>r.map(x=>x.dataset.m)')
        m=before[i]; pg.click(f'#ladder tr.click >> nth={i}'); ok(f'ladder {m}')
        after=pg.eval_on_selector_all('#ladder tr.click','r=>r.map(x=>x.dataset.m)')
        if before!=after: bug(f'ladder rows shifted after click {before}->{after}')
        if abs(float(pg.input_value('#mg'))-float(m))>1e-6: bug(f'slider {pg.input_value("#mg")} != row {m}')
    for v in ['3','7.5','22','41','50']:
        pg.fill('#mg',v); pg.dispatch_event('#mg','input'); ok('slider '+v)
    pg.focus('#ladder tr.click >> nth=0'); pg.keyboard.press('Enter'); ok('kbd')
    for k in ['1','2','3']: pg.click(f'#layers button[data-v="{k}"]'); ok('layers '+k)
    for v in ['0','15','30','50']: pg.select_option('#pitch',v); ok('pitch '+v)
    pg.click('#assume summary')
    pg.fill('#a_floor','12.3'); ok('floor 12.3'); pg.click('#presets button >> nth=0'); ok('floor preset')
    pg.fill('#a_floor','12')
    pg.fill('#r_sh_target','40'); pg.click('#types button[data-k="sh"]'); ok('target40'); print('slider @target40',pg.input_value('#mg'))
    pg.fill('#r_sh_target','15')
    def blocked(tag,sel,val):
        pg.fill(sel,val)
        if not pg.is_visible('#errs'): bug(f'{tag}: no error shown')
        if pg.text_content('#hPrice')!='—': bug(f'{tag}: stale price {pg.text_content("#hPrice")}')
        pg.click('#presets button >> nth=0')  # should do nothing
    for tag,sel,val,good in [('empty sq','#sq','','32'),('neg sq','#sq','-5','32'),('huge sq','#sq','999999','32'),('fee 100','#a_fee','100','2'),('blank oh','#a_oh','','37.1'),('neg oh','#a_oh','-50','37.1'),('neg mat','#r_sh_mat','-200','125.15'),('tax 60','#a_tax','60','7')]:
        blocked(tag,sel,val); pg.fill(sel,good); ok('recover '+tag)
    pg.fill('#sq',''); pg.fill('#a_fee','100')
    print('errors listed:',pg.inner_text('#errs').replace('\n',' | '))
    pg.fill('#sq','32'); pg.fill('#a_fee','2'); ok('recover multi')
    for v,exp in [('0','bad'),('-100','bad'),('1000','bad'),('30000','ok')]:
        pg.fill('#chk',v); c=pg.get_attribute('#chkPill','class')
        if exp not in c: bug(f'check {v}: {c}')
    pg.fill('#chk','6000'); print('chk6000:',pg.text_content('#chkPill'),'/',pg.text_content('#chkNote'))
    pg.fill('#waste','20'); pg.click('#layers button[data-v="3"]'); pg.click('#types button[data-k="ti"]'); pg.fill('#sq','80')
    pg.click('#reset'); ok('reset')
    st=pg.evaluate('[document.getElementById("waste").value,document.getElementById("sq").value,document.querySelector("#types [aria-pressed=true]").textContent,document.querySelector("#layers [aria-pressed=true]").textContent,document.getElementById("mg").value]')
    if st!=['10','32','Shingle','1','15']: bug(f'reset state {st}')
    if pg.errs: bug('js errors '+'; '.join(pg.errs))
    pg.screenshot(path='test-output/desk.png',full_page=False)
    for w in [320,375,414,768]:
        m=new(w,True); sw=m.evaluate('document.documentElement.scrollWidth')
        if sw>w: bug(f'{w}px: horizontal scroll {sw}')
        m.tap('#ladder tr.click >> nth=1')
        if abs(float(m.input_value('#mg'))-float(m.get_attribute('#ladder tr.click >> nth=1','data-m')))>1e-6: bug(f'{w}: tap ladder failed')
        m.fill('#sq','1999'); 
        sw=m.evaluate('document.documentElement.scrollWidth')
        if sw>w: bug(f'{w}px big sq: horizontal scroll {sw}')
        if w==375: m.fill('#sq','32'); m.screenshot(path='test-output/phone.png',full_page=False)
    dk=b.new_page(viewport={'width':1200,'height':900},color_scheme='dark'); dk.route('**/*fonts*',lambda r:r.abort()); dk.set_content(html); dk.screenshot(path='test-output/dark.png')
    print('TOTAL BUGS',len(P))

    b.close()
sys.exit(1 if P else 0)
