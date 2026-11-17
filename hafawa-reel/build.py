import json, math, pathlib
R = pathlib.Path(__file__).parent
m = json.loads((R/'assets/map.json').read_text())
kx = 1080/154
m.update(lon0=-22, lat0=66, kx=kx, ky=kx/math.cos(math.radians(35)))
html = (R/'src/template.html').read_text()
html = html.replace('/*FONTS*/', (R/'assets/fonts.css').read_text())
html = html.replace('/*CSS*/', (R/'src/style.css').read_text())
html = html.replace('/*MAP*/', json.dumps(m, separators=(',', ':')))
tp = R/'src/timing.json'
html = html.replace('/*TIMING*/', tp.read_text() if tp.exists() else 'null')
html = html.replace('/*APP*/', (R/'src/app.js').read_text())
(R/'index.html').write_text(html)
print('index.html', len(html)//1024, 'KB')
