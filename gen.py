with open('template.html', 'r') as f:
    temp_html = f.read()

temp_tr = '''
<tr sortA="{sortA}" sortB="{sortB}" id="{id}" class="{cls}" >
    {inner}
</tr>
'''

temp_td = '''
<td class="{name}" >
    {inner}
</td>
'''

suits =  ["wands", "swords", "cups", "coins"]
pips  =  ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "page", "knight", "queen", "king"]
trumps = ["F", "I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"]

display = {
    "F": "The Fool",
    "I": "The Magician",
    "II": "The Priestess",
    "III": "The Empress",
    "IV": "The Emperor",
    "V": "The Heirophant",
    "VI": "The Lovers",
    "VII": "The Chariot",
    "VIII": "Strength",
    "IX": "The Hermit",
    "X": "Wheel of Fortune",
    "XI": "Justice",
    "XII": "Hanged Man",
    "XIII": "Death",
    "XIV": "Temperance",
    "XV": "The Devil",
    "XVI": "The Tower",
    "XVII": "The Star",
    "XVIII": "The Moon",
    "XIX": "The Sun",
    "XX": "Judgement",
    "XXI": "The World",
    "c1": "Ace",
    "c2": "Two",
    "c3": "Three",
    "c4": "Four",
    "c5": "Five",
    "c6": "Six",
    "c7": "Seven",
    "c8": "Eight",
    "c9": "Nine",
    "c10": "Ten",
    "page": "Page",
    "knight": "Knight",
    "queen": "Queen",
    "king": "King",
    "wands": "Wands",
    "swords": "Swords",
    "coins": "Coins",
    "cups": "Cups",
}


imgn = 1
css_ls = {}
def gen_image(path, group='main', css_image_mode = True):
    global css_ls, imgn
    import base64

    data = open(path, 'rb').read() # read bytes from file
    data_base64 = base64.b64encode(data)  # encode to base64 (bytes)
    data_base64 = data_base64.decode()    # convert bytes to string

    if not css_image_mode:
        html = '<img class="card" src="data:image/jpeg;base64,' + data_base64 + '">' # embed in html
    else:
        if group not in css_ls:
            css_ls[group] = []

        html = '<img class="card" id="img_' + group + "_" + str(imgn) + '">'
        css = "img#img_" + group + "_" + str(imgn) + " { content: url(data:image/png;base64," + data_base64 + "); }"
        css_ls[group].append(css)

    imgn +=1
    return html
        

with open('ORDER','r') as f:
    order = f.read().split('\n')

import os, sys
class column():
    def __init__(self, path):
        self.path = "columns/" + path
        self.name = path

        assert os.path.exists(self.path), path

        self.dict = {}
        self.index = order.index(self.name)

        if os.path.isfile(self.path):
            with open(self.path, 'r') as fp:
                atxt = fp.read()
                for block in atxt.split("="):
                    if not block.strip():
                        continue
                    a = block.split("\n", 1)
                    fn = a[0]
                    txt = a[1]
                    temp_txt = '''
                    <p class=text>{}</p>
                    '''
                    inner = temp_txt.format(txt)
                    self.dict[fn] = inner
        else:
            for f in os.listdir(self.path):
                ext = f.split('.')[1]
                path = self.path + "/" + f
                fn = f.split('.')[0]
                if ext == 'txt':
                    with open(path, 'r') as fp:
                        txt = fp.read()

                    temp_txt = '''
                    <p class=text>{}</p>
                    '''
                    inner = temp_txt.format(txt)
                elif ext == "jpg":
                    if "_" in fn:
                        nm = self.name + "_" + fn.split("_")[1]
                    else:
                        nm = self.name + "_trump"
                    inner = gen_image(path, nm)
                else:
                    continue;

                self.dict[fn] = inner
                #print(path,fn)

def make_head(n, n2=None):
    if n2 is None:
        #major arcana
        return """
            <a href="#{id}">{txt}</a>
        """.format(id = n, txt = display[n])
    else:
        #minor arcana
        return """
            <a href="#{id}">{txt}</a>
            <br>of<br>
            <a href="#{id2}">{txt2}</a>
        """.format(
            id = n, txt = display[n],
            id2 = n2, txt2 = display[n2],
        )

def generate(ls):
    cols = []
    for d in ls:
        cols.append(column(d))

    cols.sort(key = lambda x:x.index)

    def fill(l, n):
        for c in cols:
            if n in c.dict:
                l.append(temp_td.format(name=c.name,inner=c.dict[n]))
            else:
                l.append("<td></td>")

    trs = []
    links = []
    n = 0
    for t in trumps:
        tds = [ temp_td.format(name="head", inner=make_head(t)) ]
        fill(tds, t)

        trs.append(temp_tr.format(
            sortA = n, sortB = n, 
            id=t, cls="trumps",inner = "\n".join(tds)))
        links.append("""
            <li class="trumps">
                <a href="#{}"><div>
                    <span>{}</span>
                </div></a>
            </li>""".format(t,display[t]))
        n += 1

    sn = 0
    for s in suits:
        pn = 0
        for p in pips:
            name = p+"_"+s
            tds = [ temp_td.format(name="head", inner=make_head(p,s)) ]
            fill(tds, name)
            trs.append(temp_tr.format(
                sortA = n + sn*14 + pn,
                sortB = n + pn*4 + sn,
                id = name, cls="%s %s" % (p,s),inner = "\n".join(tds)))
            links.append("""
                <li class="{} {}">
                    <a href="#{}"><div>
                        <span>{}</span>
                        of
                        <span>{}</span>
                    </div></a>
                </li>""".format(p, s, name,display[p], display[s]))
            pn += 1
        sn += 1

    css_txt = {}
    css_links = ""
    css_total = ""
    for key in css_ls:
        css_txt[key] = "\n".join(css_ls[key])
        css_links += '<link rel="stylesheet" href="{}.css">'.format(key)
        css_total += '<style>' + css_txt[key]+ "</style>"

    total = temp_html.format(rows="\n".join(trs), links = "\n".join(links), imgs=css_total )
    index = temp_html.format(rows="\n".join(trs), links = "\n".join(links), imgs=css_links )

    with open('build/total.html', 'w') as f:
        f.write(total)
    with open('build/index.html', 'w') as f:
        f.write(index)
    for k, v in css_txt.items():
        with open('build/'+k+".css", 'w') as f:
            f.write(v)

ls = os.listdir("columns")
generate(ls)

