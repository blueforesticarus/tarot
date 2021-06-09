output_split = True
output_total = True

temp_tr = '''
<tr sortA="{sortA}" sortB="{sortB}" id="{id}" class="{cls}" >
    {inner}
</tr>
'''

suits = ["wands", "swords", "cups", "coins"]
ranks = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10"]
court = ["page", "knight", "queen", "king"]
pips = ranks + court

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

with open('ORDER','r') as f:
    order = f.read().split('\n')

import os, sys
class Column():
    def __init__(self, path):
        self.path = "columns/" + path
        self.name = path

        assert os.path.exists(self.path), path

        self.html = {}
        self.css  = {}

        self.is_image = "img_" in self.name

        if os.path.isfile(self.path):
            with open(self.path, 'r') as fp:
                atxt = fp.read()

            for block in atxt.split("="):
                if not block.strip():
                    continue
                a = block.split("\n", 1)
                fn  = a[0]
                txt = a[1]
                self.html[fn] = "<p>%s</p>" % txt
        else:
            for f in os.listdir(self.path):
                path = self.path + "/" + f
                
                fn =  f.split('.')[0]
                ext = f.split('.')[1]
                if ext == 'txt':
                    with open(path, 'r') as fp:
                        txt = fp.read()
                    self.html[fn] = txt
                elif ext == "jpg":
                    html, css = self.gen_image(path)
                    self.css[fn] = css
                    self.html[fn] = html
                else:
                    continue;
    NN=0
    def gen_image(self,path):
        import base64

        data = open(path, 'rb').read() # read bytes from file
        data_base64 = base64.b64encode(data)  # encode to base64 (bytes)
        data_base64 = data_base64.decode()    # convert bytes to string

        Column.NN += 1
        imgid = "I" + str(Column.NN)
        html = '<img class="card" id="' + imgid + '">'
        css = "img#{}{{ content: url(data:image/png;base64,{}); }}".format(imgid, data_base64)
        return html, css



class suit():
    cls = "suit"

class rank():
    cls = "rank"

class court():
    cls = "court"

class Row():
    def __init__():
        pass
    
    def make_tds(self, columns):
        temp_td = '<td class="{}">{}</td>'
        self.tds = []
        for s in self.select:
            foo = "make_" + s
            if hasattr(self, foo):
                cls = s
                txt = getattr(self, foo)()
            elif self.lb in columns[s].html:
                if columns[s].is_image:
                    cls = s + " img"
                else:
                    cls = s + " txt"
                txt = columns[s].html[self.lb]
            else:
                txt = "..."
                cls = "missing"

            td = temp_td.format(cls , txt)
            self.tds.append(td)

    def make_tr(self):
        self.tr = """
            <tr {} class="{}" id="{}">{}</tr>
        """.format(self.attr, self.cls, self.lb, "".join(self.tds))

class Card(Row):
    select = ["head","info","img_rider","img_thoth","img_marseilles","img_fuego"]

    def make_link(self):
        return """
            <li class="{}">
                <a href="#{}"><div>
                    <span>{}</span>
                </div></a>
            </li>
        """.format(self.cls, self.lb, self.display)

class CardMinor(Card):
    cls = "card minors"
    def __init__(self,pip, suit):
        assert pip in pips
        assert suit in suits
        self.pip = pip
        self.suit = suit
        self.lb = pip + "_" + suit
        self.display = display[self.pip] + " of " + display[self.suit]
        self.index = pips.index(pip), suits.index(suit)
        self.attr = "sortA={} sortB={}".format(
            22 + self.index[0] + self.index[1]*14,
            22 + self.index[1] + self.index[0]*4
        )
        self.cls = CardMinor.cls + " " + self.suit + " " + self.pip

    def make_head(self):
        return """
            <a href="#{id}">{txt}</a>
            <br>of<br>
            <a href="#{id2}">{txt2}</a>
        """.format(
            id  = self.pip,  txt = display[self.pip],
            id2 = self.suit, txt2 = display[self.suit],
        )

class CardTrump(Card):
    cls = "card trumps"
    def __init__(self,lb):
        assert lb in trumps
        self.lb = lb
        self.display = display[self.lb]
        self.index = trumps.index(lb)
        self.attr = "sortA={} sortB={}".format(
            self.index,self.index
        )

    def make_head(self):
        return """
            <a href="#{}">{}</a>
        """.format(self.lb, self.display)


def generate():
    columns = {}
    for d in os.listdir("columns"):
        col = Column(d)
        columns[col.name] = col

    r_ct = []
    for t in trumps:
        r_ct.append( CardTrump(t) )

    r_cm = []
    for s in suits:
        for p in pips:
            r_cm.append( CardMinor(p, s) )

    links = ""
    for r in r_ct + r_cm:
        links += r.make_link()

    trs = ""
    for r in r_ct + r_cm:
        r.make_tds(columns)
        r.make_tr()
        trs += r.tr
    
    from collections import defaultdict 
    groups = defaultdict(list)
    for col in columns.values():
        for k, v in col.css.items():
            if "_" in k:
                suf = k.split("_")[1]
            else:
                suf = "trump"
            groups[ col.name + "_" + suf ].append(v)

    css_split = ""
    css_total = ""
    for key in groups: #TODO sort
        txt = "\n".join(groups[key])

        if output_split:
            with open('build/'+key+".css", 'w') as f:
                f.write(txt)

            css_split += '<link rel="stylesheet" href="{}.css">'.format(key)
        if output_total:
            css_total += "<style>{}</style>".format(txt) 

    with open('template.html', 'r') as f:
        temp_html = f.read()

    if output_split:
        index = temp_html.format(rows=trs, links = links, imgs=css_split )
        with open('build/index.html', 'w') as f:
            f.write(index)

    if output_total:
        total = temp_html.format(rows=trs, links = links, imgs=css_total )

    with open('build/total.html', 'w') as f:
        f.write(total)

generate()

