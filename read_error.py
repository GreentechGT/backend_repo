import re
try:
    with open('error.html', encoding='utf-8') as f:
        text = f.read()
    m = re.search(r'<textarea id="traceback_area".*?>(.*?)</textarea>', text, re.DOTALL)
    if m:
        print("TRACEBACK:")
        print(m.group(1).replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>'))
    else:
        print("NO TRACEBACK FOUND.")
        m2 = re.search(r'<div class="exception_value">([^<]+)</div>', text)
        if m2: print(m2.group(1))
except Exception as e:
    print(e)
