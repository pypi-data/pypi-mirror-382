import sys,os
scriptDir = os.path.dirname(__file__)+os.sep
rootDir=scriptDir+".."+os.sep
sys.path.append(rootDir)
import image2pdf as bd

print(bd)
bd.main()

