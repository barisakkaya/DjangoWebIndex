from django.shortcuts import render,HttpResponse
from .forms import UrlForm,UrlForm2, ContactForm
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import wordnet

def yakinAnlam(url):
    anahtarKelime = anahtarKelimeBul(url)['yeniSay'] + anahtarKelimeBul(url)['yeniSay2'] + anahtarKelimeBul(url)['yeniSay3']
    anahtarKelimeYeni = [i[0] for i in anahtarKelime]
        
    kelimeler = kelimeleriSay(url,'')['kelimeler']
    esanlam = {}
    for i in anahtarKelimeYeni:
        for syn in wordnet.synsets(i):
            for l in syn.lemmas():
                if str(l.name()).lower != i.lower():
                    for j in kelimeler:
                        if l.name() == j:
                            esanlam[i] = l.name()

    context = {
        "kelimeler" : kelimeler,
        "anahtarKelimeYeni" : anahtarKelimeYeni,
        "esanlam" : esanlam
    }    
    return context

def urlsettigns(url, etiket):
    #web sitesini parçalamak icin kullanılacak modüller:
    
    response = requests.get(url)
    html_icerigi = response.content
    soup = BeautifulSoup(html_icerigi, 'html.parser')
   
    liste = []
    if etiket != '' and etiket != 'a': 
        for i in soup.find_all(etiket):
            if len(i.get_text()) > 1: 
                liste.append(i.get_text())
    elif etiket == 'a':
        for i in soup.find_all('a'):
            liste.append(i['href'])
    else:
        test = soup.find_all()
        for j in test:
            if not j.find():
                liste.append(j.text)
    return liste

def getLinks(url):
    response = requests.get(url)
    html_icerigi = response.content
    soup = BeautifulSoup(html_icerigi, 'html.parser')
    links = [link.get('href') for link in soup.findAll('a', attrs={'href': re.compile("^https://")})]
    
    context = {
        "links" : links
    }
    return context

def similaritycalc(url):
      #web sitesini parçalamak icin kullanılacak modüller:
    response = requests.get(url)
    html_icerigi = response.content
    soup = BeautifulSoup(html_icerigi, 'html.parser')
    liste = [i.name for i in soup.find_all()]
   
    return liste

def benzerligiBul(url,url2):
    key1Sozluk,key2Sozluk = anahtarKelimeBul(url)['yeniSay'] + anahtarKelimeBul(url)['yeniSay2'] + anahtarKelimeBul(url)['yeniSay3'] , anahtarKelimeBul(url2)['yeniSay'] + anahtarKelimeBul(url2)['yeniSay2'] + anahtarKelimeBul(url2)['yeniSay3']
    key1 = [i for i in key1Sozluk]
    key2 = [i for i in key2Sozluk]
  
    #En çok kullanılan tagler:
    y1 = similaritycalc(url)
    y2 = similaritycalc(url2)
    tagSozluk1 = {}
    tagSozluk2 = {}

    for i in y1:
        if str(i) not in tagSozluk1:
            tagSozluk1[str(i)] =1
        else:
            tagSozluk1[i]+=1

    tagListe = [i for i in tagSozluk1.items()]  

    for i in y2:
        if str(i) not in tagSozluk2:
            tagSozluk2[str(i)] =1
        else:
            tagSozluk2[i]+=1

    tagListe2 = [i for i in tagSozluk2.items()]

    tagListe.sort(key=lambda x:x[1], reverse=True)
    tagListe2.sort(key=lambda x:x[1], reverse=True)

    tagListeYeni = [tagListe[i] for i in range(0,5)]
    tagListe2Yeni = [tagListe2[i] for i in range(0,5)]

    totalList = key1 + tagListeYeni
    totalList2 = key2 + tagListe2Yeni
    skor = 0 
    for i in totalList:
        for j in totalList2:
            if str(i[0]) == str(j[0]):
                skor+=1
    skorx = 0
    if len(totalList)>len(totalList2):
        skorx = len(totalList2)
    else:
        skorx = len(totalList)
    
    formul = (100*skor)/skorx
    if int(formul) == 0:
        formul = 10
    
    context = {
        "url2" : url2,
        "formul" : formul,
        "key1" : key1,
        "key2" : key2,
        "tagListeYeni" : tagListeYeni,
        "tagListe2Yeni" : tagListe2Yeni
    }
    return context

def index(request):
     return render(request,"index.html")

def kelimeleriSay(url, etiket):
    listem = urlsettigns(url,etiket)
    yeniListem = []
    for line in listem:
        line = line.rstrip('\n' + '').split(':')
        if line != ['']:
            yeniListem.append(line)
    yeniListem2 = []
    for i in yeniListem:
        for j in i:
            x = str(j).split()
            for k in x:
                yeniListem2.append(k)

    counterSozluk = {} 
    for i in yeniListem2:
        if str(i) not in counterSozluk:
            counterSozluk[str(i)] = 1
        else:
            counterSozluk[i]+=1  

    counterListe = [i for i in counterSozluk.items()]
    kelimeler = [str(i[0]) for i in counterSozluk.items()]
    
    context = {
        "kelimeler" : kelimeler,
        "counterListe" : counterListe
    }
    return context
def wordcounter(request):
    
    if request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():
           
            url = form.cleaned_data.get("url")
            say = kelimeleriSay(url, '')['counterListe']
            context = { 
                "say" : say
            }
  
            return render(request,"wordcounter2.html", context)
    else:
        
        form = UrlForm()
        context = {
            "form" : form,
            
        }
        return render(request,"wordcounter.html", context)
def anahtarKelimeBul(url):
    say = kelimeleriSay(url, '')['counterListe']
    say.sort(key=lambda x:x[1], reverse=True)
    kontrolListe = ['ama', 'fakat', 'lakin','ancak', 'yalnız', 'oysa', 'oysaki', 've',
    'ile', 'ki', 'de', 'da', 'çünkü', 'veya', 'ya', 'ise', 'yine', 'gene', '-', '',
    'için', 'her', 'a', 'for', '&', 'with', 'the', 'The', 'THE', 'in', 'up', 'is', 'and', 'or', 
    'to', 'at', 'not','=','<','>',',','.','(',')','[',']','{','}', 'With','me','Me','Hi','hi','Hi,']
    yeniSay = [say[i] for i in range(0,10) if say[i][0] not in kontrolListe]
          
    say2 = kelimeleriSay(url, 'h1')['counterListe']
    say2.sort(key=lambda x:x[1], reverse=True)
    kontrolx = 0
    if len(say2) > 10:
        kontrolx = 10
    else:
        kontrolx = len(say2)

    yeniSay2 = [say2[i] for i in range(0,kontrolx) if say2[i][0] not in kontrolListe]
                    
    total = yeniSay2 + yeniSay
    yeniSay3 = []
    if len(total) < 10:
        say3 = kelimeleriSay(url, 'h2')['counterListe']
        say3.sort(key=lambda x:x[1], reverse=True)
        kontrolx1 = 0
        if len(say3) > 10:
            kontrolx1 = 10
        else:
            kontrolx1 = len(say3)
        for i in range(0,kontrolx1):
            if say3[i][0] not in kontrolListe and not str(say3[i][0]).isdigit():
                yeniSay3.append(say3[i])
                
    context = { 
        "yeniSay" : yeniSay,
        "yeniSay2" : yeniSay2,
        "yeniSay3" : yeniSay3
    }
    return context

def keywords(request):
    if request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():
           
            url = form.cleaned_data.get("url")
            x = anahtarKelimeBul(url)
  
            return render(request,"keywords2.html", x)

    else:
        
        form = UrlForm()
        context = {
            "form" : form,
            
        }
        return render(request,"keywords.html", context)

def similarity(request):
    
    if request.method == "POST":
        form = UrlForm2(request.POST)
        if form.is_valid():
           
            url = form.cleaned_data.get("url")
            url2 = form.cleaned_data.get("url2")
  
            return render(request,"similarity2.html", benzerligiBul(url,url2))

    else:
        form = UrlForm2()
        context = {
            "form" : form, 
        }
        return render(request,"similarity.html", context)

def cozumleme(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            webkume = form.cleaned_data.get("webkume")
            webKumeList = str(webkume).split()

            x = []
            x2 = []
            x3 = []
            liste1 = [benzerligiBul(url, i) for i in webKumeList]
            yakinAnlamBul = [yakinAnlam(i)['esanlam'] for i in webKumeList]

            for i in range(0, len(liste1)):
                x.append(liste1[i]['url2'])
                x.append(liste1[i]['key1'])
                x.append(liste1[i]['key2'])
                x.append(liste1[i]['tagListeYeni'])
                x.append(liste1[i]['tagListe2Yeni'])
                x.append(liste1[i]['formul'])
                x.append(yakinAnlamBul[i])

            func = [getLinks(i)['links'] for i in webKumeList]
           
            
            yeniFunc = []
            sayim = 0
            while sayim<len(func):
                if len(func[sayim]) >= 2:
                    for j in range(0, 2):
                        yeniFunc.append(func[sayim][j])
                        
                elif len(func[sayim]) >= 1 and len(func[sayim]) < 2:
                    for j in range(0, 1):
                        yeniFunc.append(func[sayim][j])
                sayim+=1
            liste2 = [benzerligiBul(url, i) for i in yeniFunc]
            yakinAnlamBul2 = [yakinAnlam(i)['esanlam'] for i in yeniFunc]
        
            for i in range(0, len(liste2)):
                x2.append(liste2[i]['url2'])
                x2.append(liste2[i]['key1'])
                x2.append(liste2[i]['key2'])
                x2.append(liste2[i]['tagListeYeni'])
                x2.append(liste2[i]['tagListe2Yeni'])
                x2.append(liste2[i]['formul'])
                x2.append(yakinAnlamBul2[i])

            func2 = [getLinks(i)['links'] for i in yeniFunc]

            yeniFunc2 = []
            sayim2 = 0
            while sayim2<len(func2):
                if len(func2[sayim2]) >= 2:
                    for j in range(0, 2):
                        yeniFunc2.append(func2[sayim2][j])
                elif len(func2[sayim2]) >= 1 and len(func2[sayim2]) < 2:
                    for j in range(0, 1):
                        yeniFunc2.append(func2[sayim2][j])
                sayim2+=1
            liste3 = [benzerligiBul(url, i) for i in yeniFunc2]
            yakinAnlamBul3 = [yakinAnlam(i)['esanlam'] for i in yeniFunc2]
        
            for i in range(0, len(liste3)):
                x3.append(liste3[i]['url2'])
                x3.append(liste3[i]['key1'])
                x3.append(liste3[i]['key2'])
                x3.append(liste3[i]['tagListeYeni'])
                x3.append(liste3[i]['tagListe2Yeni'])
                x3.append(liste3[i]['formul'])
                x3.append(yakinAnlamBul3[i])
            
            context = {
                "webKumeList" : webKumeList,
                "liste1" : liste1,
                "x" : x,
                "x2" : x2,
                "x3" : x3
            }

            return render(request,"cozumleme2.html", context)

    else:
        form = ContactForm()
        context = {
            "form" : form,            
        }
        return render(request,"cozumleme.html", context)

def analysis(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            webkume = form.cleaned_data.get("webkume")
            webKumeList = str(webkume).split()

            x = []
            x2 = []
            x3 = []
            sozluk = {}
            liste1 = [benzerligiBul(url, i) for i in webKumeList]
            for i in range(0, len(liste1)):
                x.append(liste1[i]['url2'])
                x.append(liste1[i]['key1'])
                x.append(liste1[i]['key2'])
                x.append(liste1[i]['tagListeYeni'])
                x.append(liste1[i]['tagListe2Yeni'])
                x.append(liste1[i]['formul'])
                sozluk[liste1[i]['url2']] = liste1[i]['formul']

            func = [getLinks(i)['links'] for i in webKumeList]
            
            yeniFunc = []
            sayim = 0
            while sayim<len(func):
                if len(func[sayim]) >= 2:
                    for j in range(0, 2):
                        yeniFunc.append(func[sayim][j])
                        
                elif len(func[sayim]) >= 1 and len(func[sayim]) < 2:
                    for j in range(0, 1):
                        yeniFunc.append(func[sayim][j])
                sayim+=1
            liste2 = [benzerligiBul(url, i) for i in yeniFunc]        
            for i in range(0, len(liste2)):
                x2.append(liste2[i]['url2'])
                x2.append(liste2[i]['key1'])
                x2.append(liste2[i]['key2'])
                x2.append(liste2[i]['tagListeYeni'])
                x2.append(liste2[i]['tagListe2Yeni'])
                x2.append(liste2[i]['formul'])
                sozluk[liste2[i]['url2']] = liste2[i]['formul']

            func2 = [getLinks(i)['links'] for i in yeniFunc]

            yeniFunc2 = []
            sayim2 = 0
            while sayim2<len(func2):
                if len(func2[sayim2]) >= 2:
                    for j in range(0, 2):
                        yeniFunc2.append(func2[sayim2][j])
                elif len(func2[sayim2]) >= 1 and len(func2[sayim2]) < 2:
                    for j in range(0, 1):
                        yeniFunc2.append(func2[sayim2][j])
                sayim2+=1
            liste3 = [benzerligiBul(url, i) for i in yeniFunc2]
        
            for i in range(0, len(liste3)):
                x3.append(liste3[i]['url2'])
                x3.append(liste3[i]['key1'])
                x3.append(liste3[i]['key2'])
                x3.append(liste3[i]['tagListeYeni'])
                x3.append(liste3[i]['tagListe2Yeni'])
                x3.append(liste3[i]['formul'])
                sozluk[liste3[i]['url2']] = liste3[i]['formul']
            
            listeSozluk = [i for i in sozluk.items()]
            listeSozluk.sort(key=lambda x:x[1], reverse=True)

            context = {
                "webKumeList" : webKumeList,
                "liste1" : liste1,
                "x" : x,
                "x2" : x2,
                "x3" : x3,
                "listeSozluk" : listeSozluk
            }

            return render(request,"analysis2.html", context)


    else:
        form = ContactForm()
        context = {
            "form" : form,            
        }
        return render(request,"analysis.html", context)