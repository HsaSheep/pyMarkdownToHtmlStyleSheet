import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
import os
import os.path
import sys
import re
import base64
import pdfkit
import tkinter
import tkinter.filedialog


# ファイル選択ダイアログ
def file_select(init_path):
    root = tkinter.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    if not os.path.isdir(init_path):
        init_path = os.getcwd()
    return tkinter.filedialog.askopenfilename(filetypes = [('Markdownファイル','*.md')], title = "Markdownファイルを選択", initialdir = init_path)


# 画像ファイル→ Base64 エンコード
def imageToB64encode(img_path):
    with open(img_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def mark_to_html(path:str):
    # Pygmentsでハイライト用のスタイルシートを作成
    #style = HtmlFormatter(style='solarized-dark').get_style_defs('.codehilite')
    
    # スタイルシートファイルの読み込み
    s_path = 'md2pdf.css'
    if not os.path.isfile(path):
        print(".cssファイルがありません。 Path: " + s_path)
    with open(s_path, mode='r', encoding='UTF-8') as sf:
        style = sf.read()
    #print(style)

    # マークダウンファイルの読み込み
    if not os.path.isfile(path):
        print(".mdファイルがありません。 Path: " + path)
    f = open(path, mode='r', encoding='UTF-8')
    with f:
        text = f.read()
        # Markdown の import 文を除去
        text = re.sub('@import ".+"\n', '', text)
        # HTMLに変換
        body = markdown.Markdown(extensions=['extra', 'codehilite']).convert(text)
        
        # 画像は、base64 エンコードして <img src=data:image/png;base64,base64エンコード文字列"/> にする。
        for imgtag in re.findall('<img .* src=".+"', body):
            s = re.search('src=".+"', imgtag).group(0).replace('src="', '').replace('"', '')
            s = os.path.split(path)[0] + os.path.sep + s
            print(s)
            imgval = re.search('<img .* ', imgtag).group(0)
            imgval += 'src="data:image/' + s[-3:] + ';base64,' + imageToB64encode(s) + '"'
            body = body.replace(imgtag, imgval)
        
        # HTML書式に合わせる
        html = '<html lang="ja"><meta charset="utf-8">'
        html += '<style>' + style + '</style>'
        html += '<body>'
        # Pygmentsで作成したスタイルシートを取り込む
        #html += '<style>{}</style>'.format(style)
        # Tableタグに枠線を付けるためにスタイルを追加
        #html += '''<style> table,th,td { 
        #    border-collapse: collapse;
        #    border:1px solid #333; 
        #    } </style>'''
        html += body + '</body></html>' 
        return html


def html_to_pdf(path:str, html:str):
    """
    html : str HTML
    """
    # wkhtmltopdfの実行ファイルのパスの指定
    # path_wkhtmltopdf = os.getcwd() + r'\wkhtmltox\bin\wkhtmltopdf.exe'
    path_wkhtmltopdf = os.environ['wkhtmltopdf'] + r'\wkhtmltopdf.exe'
    if not os.path.isfile(path_wkhtmltopdf):
        print("wkhtmltopdf.exeがありません。 Path: " + path_wkhtmltopdf)
    #print("wkhtmltopdf: " + path_wkhtmltopdf)
    
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    options = {
     'page-size': 'A4',
     'margin-top': '0.75in',
     'margin-right': '0.75in',
     'margin-bottom': '0.75in',
     'margin-left': '0.75in',
     'encoding': "UTF-8"
    }
    # HTML→PDF変換の実行
    pdfkit.from_string(html, outputfile, configuration=config, options=options)
    #pdfkit.from_string(html, outputfile)


# if __name__ == '__main__':
#path = ''
path = file_select("")

if path == '':
    print("Cancel.")
    sys.exit()
else:
    path = os.path.abspath(path)
    outputfile = os.path.split(path)[0] + os.path.sep
    outputfile += os.path.splitext(os.path.basename(path))[0] + '.pdf'
    print(" Input: " + path)
    print("Output: " + outputfile)
    f_path = 'md2pdf.path'
    with open(f_path, mode='w', encoding='utf-8') as f:
        f.writelines([path+'\n', outputfile+'\n'])
        f.close()
    
    html_to_pdf(outputfile, mark_to_html(path))
    print("\n\n --- DONE ---")
