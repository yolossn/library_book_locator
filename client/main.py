import tkinter as tk
from tkinter import StringVar,IntVar,ttk,PhotoImage
from tkinter import *
import MFRC522
import requests
import time
FF_FONT=("action man",22) #tk font
F_FONT=("action man",14) #tk font1
S_FONT=("tahoma",10) #tk font2
sbookName=None #keyword 
searchTag=None #tag corresponding to selected book
misplaced=[] #list of misplaced books
continue_read = False #Control Variable for tk function
column='None' #current column
colBooks=[] #get books to be placed in current column
counter=0 #count of misplaced books
class Application(tk.Tk): #This is the main window
    def __init__(self,*args):
        tk.Tk.__init__(self,*args)
        tk.Tk.wm_title(self,"Library Book Locator")
        container=tk.Frame(self)
        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        self.frames={}
        for fram in (home,searching):
            frame=fram(container,self)
            self.frames[fram]=frame
            frame.grid(row=0,column=0,sticky="nsew")
        self.show_frame(home)
        #self.show_frame(searching)
        
    def show_frame(self,cont): # function to show the frame in the main window
        frame=self.frames[cont]
        frame.tkraise()
    
class home(tk.Frame): #This is the Landing frame
    def __init__(self,parent,controller):
        bookName=StringVar()
        tk.Frame.__init__(self,parent)
        def setBookName(a):
            labelTitle.pack_forget()
            logoLabel.pack_forget()
            keywords.pack_forget()
            keywordsEntry.pack_forget()
            searchKeywordButton.pack_forget()
            def remove():
                label.pack_forget()
                changeButton.pack_forget()
                show()
            def show():
                labelTitle.pack(pady=10,padx=10)
                logoLabel.pack(pady=10,padx=10)
                keywords.pack(pady=10,padx=10)
                keywordsEntry.pack(pady=10,padx=10)
                searchKeywordButton.pack(pady=10,padx=10)
            global sbookName
            book=StringVar()
            sbookName=a
            apiResults=requests.get('http://librarybookscanner.herokuapp.com/api/search?book='+sbookName)
            print(apiResults.text)
            if apiResults.status_code==200:
                global searchTag
                def contSearch():
                    global searchTag
                    searchTag=book.get()
                    print('searching for book'+searchTag)
                    controller.show_frame(searching)    
                
                apiResults=apiResults.json()
                apiBookResults=[{'name':apiResults[i]['bookName'],'id':apiResults[i]['tag']} for  i in range(0,len(apiResults))]
                label=tk.Label(self,text="SELECT BOOK",font=F_FONT)
                label.pack(padx=10,pady=4)
                booksPic=PhotoImage(file='books.png')
                booksPicLabel=tk.Label(self,image=booksPic)
                booksPicLabel.image=booksPic
                booksPicLabel.pack(padx=10,pady=10)
                for i in apiBookResults:
                    bookResults=ttk.Radiobutton(self,text=i['name'],variable=book,value=i['id'])
                    bookResults.pack(padx=10,pady=3)
                searchButton=ttk.Button(self,text="Search",command=lambda:contSearch())
                searchButton.pack(padx=10,pady=10)
            elif apiResults.status_code==404:
                label=tk.Label(self,text="No book found for the given Keyword",font=F_FONT)
                label.pack(padx=10,pady=4)
                changeButton=tk.Button(self,text="Change Keyword",command=lambda:remove())
                changeButton.pack(padx=10,pady=10)    
        labelTitle=tk.Label(self,text="LIBRARY BOOK LOCATOR",font=FF_FONT)
        logo=PhotoImage(file='download.png')
        logoLabel=tk.Label(self,image=logo)
        logoLabel.image=logo
        keywords=tk.Label(self,text="Keywords",font=F_FONT)
        keywordsEntry=tk.Entry(self,textvariable=bookName,width=10)
        searchKeywordButton=ttk.Button(self,text="Search",command=lambda:setBookName(bookName.get()))
        #Packing 
        labelTitle.pack(pady=10,padx=10)
        logoLabel.pack(pady=10,padx=10)
        keywords.pack(pady=10,padx=10)
        keywordsEntry.pack(pady=10,padx=10)
        searchKeywordButton.pack(pady=10,padx=10)
        
class searching(tk.Frame):#searching frame
    def __init__(self,parent,controller):
        global column
        tk.Frame.__init__(self,parent)
        searcgLabel=tk.Label(self,)
        searchPic=PhotoImage(file='searching.gif')
        searchPicLabel=tk.Label(self,image=searchPic)
        searchPicLabel.image=searchPic
        searchPicLabel.pack(padx=10,pady=10)
        colLabel=tk.Label(self,text='Column:'+column,font=F_FONT)
        colLabel.pack(padx=10,pady=4)
        def scanColumn():
            global column,colBooks
            while True:
                (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
                (status,backData) = MIFAREReader.MFRC522_Anticoll()
                if status == MIFAREReader.MI_OK:
                  #print ("Card read UID: "+str(backData[0])+","+str(backData[1])+","+str(backData[2])+","+str(backData[3])+","+str(backData[4]))
                  readTag='{:02x}'.format(backData[0]).upper()+'-{:02x}'.format(backData[1]).upper()+'-{:02x}'.format(backData[2]).upper()+'-{:02x}'.format(backData[3]).upper()
                  print('column:',readTag)
                  if len(backData)>0:
                      column=readTag
                      colBooks=requests.get('http://librarybookscanner.herokuapp.com/api/books/'+column).json()
                      print('col books:',colBooks)
                      z=requests.get('http://librarybookscanner.herokuapp.com/api/row/'+column)
                      if z.status_code!=200:
                          continue
                      colLabel.configure(text=z.text)
                      break
        def endRead():
          global continue_read,counter
          continue_read= False
          global misplaced
          print (misplaced)
          MIFAREReader.GPIO_CLEEN()
          label=tk.Label(self,text="No of books searched:0",font=F_FONT)
          label.pack(padx=10,pady=4)
          label.configure(text="No of books searched:"+str(counter))
        def startRead():
            global continue_read
            continue_read=True
        scanColButton=ttk.Button(self,text='Scan Column',command=lambda:scanColumn())
        scanColButton.pack(padx=10)
        beginButton=ttk.Button(self,text='Begin Scan',command=lambda:startRead())
        beginButton.pack(padx=10)
        endButton=ttk.Button(self,text='End Scan',command=lambda:endRead())
        endButton.pack(padx=10)

            
def checkBookAndPosition(tag):
    global searchTag,colBooks,column
    print(searchTag)
    apiResponse=requests.get('http://librarybookscanner.herokuapp.com/api/id/'+tag)
    if apiResponse.status_code==200:
        bookInfo=apiResponse.json()
        print('###bookCol,searchCol '+bookInfo['row']['rowId']+' '+column)
        print('book col,scan col\t',bookInfo['row']['rowId'],column)
        if tag not in colBooks:
            global misplaced
            misplaced.append({bookInfo['bookName']:bookInfo['row']['rowName']})
            print('misplaced request '+'http://librarybookscanner.herokuapp.com/api/misplaced?row='+column+'&book='+tag)
            v=requests.get('http://librarybookscanner.herokuapp.com/api/misplaced?row='+column+'&book='+tag)
            print(v.text)
        print('###,booktag,searchtag '+bookInfo['tag']+' '+searchTag)
        if bookInfo['tag']==searchTag:
            print('book found')
            popup=tk.Toplevel()
            popup.title('Success')
            popup.geometry('150x150')
            successLabel=tk.Label(popup,text='Book Found',font=F_FONT)
            successLabel.pack(padx=5,pady=5)
def read():
    global continue_read
    #print(continue_read)
    if continue_read:
        global column
        global counter
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        (status,backData) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            #print ("Book scanned: "+str(backData[0])+","+str(backData[1])+","+str(backData[2])+","+str(backData[3])+","+str(backData[4]))
            readTag='{:02x}'.format(backData[0]).upper()+'-{:02x}'.format(backData[1]).upper()+'-{:02x}'.format(backData[2]).upper()+'-{:02x}'.format(backData[3]).upper()
            print("Book scanned: "+readTag)
            counter+=1
            checkBookAndPosition(readTag)
    app.after(1000,read)
                

if __name__=='__main__':
    app= Application()
    MIFAREReader = MFRC522.MFRC522()
    app.after(1000,read)
    app.mainloop()
    
