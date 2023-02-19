from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter import Frame
from xml.dom import minidom
import pyAesCrypt
import pathlib
import os
import sys



window=Tk()
window.geometry("400x300")
window.title("PyEncry")
window.resizable(width=False, height=False)

wFrame=Frame(window,bg="#FAFAEB")
wFrame.pack(side="top",fill="both",expand=True)

statusLabel=Label(window,text="Welcome",bd=1,relief=SUNKEN,anchor=W)
statusBar=statusLabel
statusBar.pack(side=BOTTOM,fill=X)
doesVar=IntVar()
doesVar.set(0)
firstGen=True
selectedFiles=[]
outPath=""
infoPath=""

def openFileButton():
    statusLabel["text"]=""
    global openFiles
    global selectedPath
    accTypes=[('Files','*.bin *.jpg *.jpeg *.png *.gif *.mp3 *.mp4 *.mkv *.h264 *.avi *.3gp *.flv *.mov *.mpeg *.mpg *.webm *.wmv *.pdf *.txt *.exe')]
    openFiles=filedialog.askopenfilenames(filetypes=accTypes)
    if len(openFiles)>0:
        textBox.delete(0,END)
        selectedPath=pathlib.PurePath(openFiles[0]).parent
        global selectedFiles
        selectedFiles=[]
        treeView.delete(*treeView.get_children())
        selectedFiles.append(('Files Path: ',selectedPath))
        global firstGen
        if firstGen:
            doesMenu.add_radiobutton(label="Encryp",value=2,command=doesButtonEvent,variable=doesVar)
            doesMenu.add_radiobutton(label="Decryp",value=3,command=doesButtonEvent,variable=doesVar)
            firstGen=False

        for fileName in openFiles:
            selectedFileSize=round((os.path.getsize(fileName))/1024,1)
            onlyName=pathlib.PurePath(fileName).name
            selectedFiles.append((onlyName,f'{selectedFileSize} KB'))
            
        
        for selectedFile in selectedFiles:
            fileIndex=selectedFiles.index(selectedFile)
            treeView.insert('',fileIndex,values=selectedFile)
            
    else:
        doesVar.set(None)
    


def encrypButton():
     
     doesVar.set(None)
     textBox.config(show="*")
     global password
     global selectedFiles
     
     checkExt=pathlib.Path(selectedFiles[1][0]).suffix
     password=textBox.get()
     
     
     if not password:
        statusLabel["text"]="Please write password and again click Encryp"
        
     else:
        if checkExt!=".bin":

            statusLabel["text"]=""
            selectedFiles.clear()
            treeView.delete(*treeView.get_children())
            selectedFiles.append(('Files Path: ',selectedPath))
            
            xmlDoc = minidom.Document()
            xEncry = xmlDoc.createElement('xEncry') 
            xmlDoc.appendChild(xEncry)
    
            pathChild = xmlDoc.createElement('path')
            pathChild.setAttribute('value', str(selectedPath))
            xEncry.appendChild(pathChild)
            
            fileList=xmlDoc.createElement("fileList")
            xEncry.appendChild(fileList)
            

            for fileName in openFiles:
                fileIndex=openFiles.index(fileName)
                encFile=pathlib.PurePath(fileName)
                encName="{}\\DATA{}.bin".format(selectedPath,fileIndex)
                fileName=encName
                os.rename(encFile,encName)
                onlyName=pathlib.PurePath(encFile).name

                memFile=xmlDoc.createElement("fileName")
                memFile.setAttribute('name', onlyName)
                #bytesValue=bytes()
                with open(encName, 'r+b') as f:
                    f.seek(0)
                    bytesValue = f.read(16)
                    
                    print(bytesValue)
                    integerBytes=int.from_bytes(bytesValue, byteorder=sys.byteorder) 
                    memFile.setAttribute('value',str(integerBytes))
                    f.seek(0)
                    f.write(b'\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21\x21')
                fileList.appendChild(memFile)
                
                encFileSize=round((os.path.getsize(encName))/1024,1)
                onlyName=pathlib.PurePath(encName).name
                selectedFiles.append((onlyName,f'{encFileSize} KB'))

            xml_str = xmlDoc.toprettyxml(indent ="\t")
            global infoPath
            infoPath=str(selectedPath.joinpath("SYS.xml"))
            xmlFile=open(infoPath, "w")
            xmlFile.write(xml_str)
            xmlFile.close()
            EncrypXML()

            for selectedFile in selectedFiles:
                fileIndex=selectedFiles.index(selectedFile)
                treeView.insert('',fileIndex,values=selectedFile)

            statusLabel["text"]="Files Encrypted"
        else:
            messagebox.showerror("Error", "You cannot encrypt encrypted files")

        
        
     

def decrypButton():
    doesVar.set(None)
    textBox.config(show="*")
    global password
    global selectedFiles
    password=textBox.get()

    
    if not password:
        statusLabel["text"]="Please write password and again click Decryp"
    else:

        if(DecrypXML()):
            readXML=minidom.parse(infoPath)
            xmlFileNames = readXML.getElementsByTagName("fileName")
            xmlPath=readXML.getElementsByTagName("path")[0]
            dencPath=xmlPath.getAttribute('value')
            dencFiles=[]
            dencFiles.append(('Files Path: ',dencPath))
            treeView.delete(*treeView.get_children())
            

            for xmlFile in xmlFileNames:
                xmfileIndex=xmlFileNames.index(xmlFile)+1
                realFile=str(selectedPath.joinpath(selectedFiles[xmfileIndex][0]))
                endPath=pathlib.Path("{}\\{}".format(selectedPath,xmlFile.getAttribute("name")))
                with open(realFile, 'r+b') as f:
                    intData=int(xmlFile.getAttribute("value"))
                    byteDatas=intData.to_bytes(16,byteorder=sys.byteorder)
                    f.seek(0)
                    f.write(byteDatas)
                selectedFileSize=round((os.path.getsize(realFile))/1024,1)
                onlyName=pathlib.PurePath(endPath).name
                dencFiles.append((onlyName,f'{selectedFileSize} KB'))
                os.rename(realFile,endPath)
                
            
            selectedFiles.clear()
            selectedFiles=dencFiles

            for secFile in dencFiles:
                fileIndex=dencFiles.index(secFile)
                treeView.insert('',fileIndex,values=secFile)
                
                
            statusLabel["text"]="Files Decrypted"
            os.remove(infoPath)

def EncrypXML():
    bufferSize=512*1024
    global outPath
    outPath=pathlib.Path(infoPath).stem+".aes"
    outPath=str(selectedPath.joinpath(outPath))
    pyAesCrypt.encryptFile(infoPath,outPath,password,bufferSize)
    os.remove(infoPath)

def DecrypXML():
    password=textBox.get()
    bufferSize=512*1024
    global outPath
    global infoPath
    if not outPath:
        outPath=str(pathlib.Path(selectedPath.joinpath("SYS.aes")))
        infoPath=str(pathlib.Path(selectedPath.joinpath("SYS.xml")))
    
    if ((pathlib.Path(outPath)).is_file()):
        try:
            pyAesCrypt.decryptFile(outPath,infoPath,password,bufferSize)
            os.remove(outPath)
            print("File Decrypted: {}".format(infoPath))
            return True
        except ValueError:
            messagebox.showerror("Error", "Invalid or wrong password")
            return False
    else:
        return False


        

    



def doesButtonEvent():
    selectedVar=doesVar.get()
    match selectedVar:
        case 1:
            openFileButton()
        case 2:
            encrypButton()
        case 3:
            decrypButton()
        case _:
            print("Non Select")


textBox=Entry(wFrame,width=52)
textBox.grid(row=0,column=0,padx=1,pady=1)

doesButton=ttk.Menubutton(wFrame,text="Options ")
doesMenu=Menu(doesButton,tearoff=0)

OpenBtn=StringVar()
doesMenu.add_radiobutton(label="Open",value=1,command=doesButtonEvent, variable=doesVar)

EncrypBtn=StringVar()
DecrypBtn=StringVar()


doesButton["menu"]=doesMenu
doesButton.grid(row=0,column=1,padx=1,pady=1)


treeColumns=('file_path','file_size')
treeView=ttk.Treeview(wFrame,columns=treeColumns,show='headings')
treeView.heading('file_path', text="Name")
treeView.heading('file_size',text="Data")
treeView.grid(columnspan=2,row=1,padx=1,pady=1)


window.mainloop()