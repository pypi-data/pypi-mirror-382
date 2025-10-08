import os
import sys
# pip install PyMuPDF
import fitz
scriptDir = os.path.dirname(__file__)+os.sep
rootDir=scriptDir+".."+os.sep
sys.path.append(rootDir)
from src.bscommon import Com
from src.bscommon import Ssh
from src.bscommon import SysTask
sys.path.remove(rootDir)



def ImageToPdf(imagesDir, fullPdfFileName,suffix=('.png', '.jpg', '.jpeg', '.bmp')):
    doc = fitz.open()
    img_files = [f for f in os.listdir(imagesDir) 
        if f.lower().endswith(suffix)]
    for imgName in sorted(img_files):
        imgPath = os.path.join(imagesDir, imgName)
        imgDoc = fitz.open(imgPath)
        imgPdfBytes = imgDoc.convert_to_pdf()
        imgPdf = fitz.open("pdf", imgPdfBytes)
        doc.insert_pdf(imgPdf)
    doc.save(fullPdfFileName)
    doc.close()
    print(f"成功将 {len(img_files)} 张图片转换到 {fullPdfFileName} 文件中。")

if __name__ == "__main__":
    imagesPath = "/Users/daiyanbing/Downloads/images/"  # 图片文件夹路径
    pdfFileName = "output.pdf"  # 输出PDF路径
    ImageToPdf(imagesPath, imagesPath+pdfFileName)