import xml.etree.ElementTree as ET
from io import StringIO
import sys

if __name__ == '__main__':
#    infile = '/home/fburkhardt/tmp/tmp.xml'
    infile = sys.argv[1]
    with open(infile) as f:
        xml = f.read()
    # get rid of the namespace
    it = ET.iterparse(StringIO(xml))
    for _, el in it:
        prefix, has_namespace, postfix = el.tag.partition('}')
        if has_namespace:
            el.tag = postfix  # strip all namespaces
    root = it.root
    st = 0.0
    pause = 'SILENT PAUSES'
    for w in root.findall('p/s/phrase/t'):
        word = w.text.strip()
        s = w[0]
        ps = s.findall('ph')
        duration = float(ps[0].get('d'))
        end = float(ps[-1].get('end'))
        start = end-duration
        print('%s %s %s' % (word, st, end))
        st += end