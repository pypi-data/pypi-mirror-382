import os
import sys
import argparse
# pip install PyMuPDF
import fitz
scriptDir = os.path.dirname(__file__)+os.sep
rootDir=scriptDir+".."+os.sep
sys.path.append(rootDir)
sys.path.remove(rootDir)

# 解析命令行参数
def GetArgs():
    parser = argparse.ArgumentParser(description='Python参数解析示例')
    
    # 位置参数
    parser.add_argument('imagesPath', help='图片所在路径')
    
    # 可选参数
    parser.add_argument('-n', '--name', default='output.pdf',
                      help='生成Pdf文件名称 (默认: output.pdf)')
    parser.add_argument('-o', '--outputdir', default='',
                      help='输出文件路径 (默认: 图片所在路径)')
    parser.add_argument('-e', '--extNames', default='.png,.jpg,.jpeg,.bmp',
                      help='只读取符合要求的图片 (默认: .png,.jpg,.jpeg,.bmp)')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='启用详细输出模式(默认: 关闭)')
    
    args=parser.parse_args()
    args.imagesPath=args.imagesPath + ("" if args.imagesPath.endswith(os.sep) else os.sep)
    args.outputdir=args.outputdir if args.outputdir else args.imagesPath
    args.extNames=tuple(args.extNames.split(","))
    return args

# 图片转PDF
def ImageToPdf(imagesDir, fullPdfFileName,suffix=('.png', '.jpg', '.jpeg', '.bmp')):
    imgFiles = [f for f in os.listdir(imagesDir) 
        if f.lower().endswith(suffix)]
    imgCount=len(imgFiles)
    if(imgCount==0):
        print("没有找到对应图, 无法生成。")
        return
    doc = fitz.open()
    for imgName in sorted(imgFiles):
        imgPath = os.path.join(imagesDir, imgName)
        imgDoc = fitz.open(imgPath)
        imgPdfBytes = imgDoc.convert_to_pdf()
        imgPdf = fitz.open("pdf", imgPdfBytes)
        doc.insert_pdf(imgPdf)
    doc.save(fullPdfFileName)
    doc.close()
    print(f"成功将 {imgCount} 张图片转换到 {fullPdfFileName} 文件中。")

def main():
    args = GetArgs()
    imagesPath = args.imagesPath    # 图片文件夹路径
    outputDir = args.outputdir
    pdfFileName = args.name         # 输出PDF路径
    suffix=args.extNames
    print(suffix)
    verbose = args.verbose          # 是否输出详细信息
    ImageToPdf(imagesPath, outputDir+pdfFileName,suffix)

if __name__ == "__main__":
    main()