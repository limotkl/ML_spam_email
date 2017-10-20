import re
import os
import copy
import math
import sys

sys.argv[1]

hamset = []
spamset = []
stopset = []
numham = 0 
numspam = 0
indiham = 0
indispam = 0
Pham = 0 
Pspam = 0 

def wordFreq(vocabList,inputSet):
    returnVec=[0]*len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)]+=1
    return returnVec
#delet stopwords
def delStop(wordset,wordlist,stopset):
    indi = 0
    wordsettemp = copy.copy(wordset)
    for words in wordset:
        for word in stopset:
            if words == word:
                wordsettemp.remove(words)
    #get new wordset frequency without stopword
    Vec=[0]*len(wordsettemp)
    for word in wordlist:
        if word in wordsettemp:
            Vec[wordsettemp.index(word)]+=1
    for x in Vec:
        indi = indi + int(x)
    return wordsettemp,Vec,indi
#Ignore punctuation & special characters ,normalize words by converting them to lower case, converting plural words to singular
def getword(SString):
    mailwords = re.split(r'\W*', SString)
    #if len(word) > 12 it's very likely that this is not a meaningful word so ignore it  
    lowwords =[word.lower() for word in mailwords if(len(word) > 2 and len(word) < 12 and word.isalpha())]
    slow = []
    #converting plural words to singular
    for word in lowwords:
        if word[-1] == 's':
            #print(word[:-1])
            slow.append(word[:-1])
        else:
            #print(word)
            slow.append(word)
    return slow

def training ( path ,stopset,flag):
    wordlist = []
    wordset = []
    wordVec = []
    indiword = 0
    num = 0
    pathDir =  os.listdir(path)
    for allDir in pathDir:
        num+=1
        f = open(path +allDir)
        s=f.read()
        wordlisttemp = []
        wordlisttemp = getword(s)
        wordlist.extend(wordlisttemp)
    wordset = list(set(wordlist))
    wordVec=[0]*len(wordset)
    #get word frequency
    for word in wordlist:
        if word in wordset:
            wordVec[wordset.index(word)]+=1
    for x in wordVec:
        indiword = indiword + int(x)

    if flag is 0:
        return wordset,wordVec,indiword,num
    else:#deled stop words
        wordset,wordVec,indiword = delStop(wordset,wordlist,stopset)
        return wordset,wordVec,indiword,num

def test (path,hamset,spamset,hamVec,spamVec,sumham,sumspam):
    ham = 0 
    spam = 0

    pathDir =  os.listdir(path)
    for allDir in pathDir:
        f = open(path + allDir)
        s=f.read()
        mailwords = re.split(r'\W*', s)
        
        inputstring =[word.lower() for word in mailwords if(len(word) > 2 and word.isalpha())]
        inputstringset = list(set(inputstring))
        inputVec=[0]*len(inputstringset)

        for word in inputstring:
            if word in inputstringset:
                inputVec[inputstringset.index(word)]+=1

        Ptestham = [0]*len(inputstringset)
        Ptestspam = [0]*len(inputstringset)
        #use multinomial Naive Bayes algorithm to calculate
        for testword in inputstringset:
            if testword in hamset :
                fenzi = hamVec[hamset.index(testword)]+1
                Ptestham[inputstringset.index(testword)] = float(fenzi)/float(sumham)
            else:
                fenzi = 1
                Ptestham[inputstringset.index(testword)] = float(fenzi)/float(sumham)

        for testword in inputstringset:
            if testword in spamset:
                fenzi = spamVec[spamset.index(testword)]+1
                Ptestspam[inputstringset.index(testword)] = float(fenzi)/float(sumspam)
            else:
                fenzi = 1
                Ptestspam[inputstringset.index(testword)] = float(fenzi)/float(sumspam)
        P1 = math.log(Pham)
        P0 = math.log(Pspam)
        for word in inputstringset:
            # P1 = P1 * (Ptestham[inputstringset.index(word)]** inputVec[inputstringset.index(word)])
            # P0 = P0 * (Ptestspam[inputstringset.index(word)]** inputVec[inputstringset.index(word)])
            P1 = P1 + math.log((Ptestham[inputstringset.index(word)])) * inputVec[inputstringset.index(word)]
            P0 = P0 + math.log((Ptestspam[inputstringset.index(word)])) * inputVec[inputstringset.index(word)]
        if P1  > P0 :
            ham +=1
        else:
            spam +=1
    return  ham , spam


if __name__ == '__main__': 

    f = open(sys.argv[1] + 'stopWords.txt')
    s=f.read()
    wordlist = []
    wordlist = getword(s)
    stopset = list(set(wordlist))

    hamset,hamVec,indiham,numham = training(sys.argv[2]+'/ham/',stopset,0) 
    spamset,spamVec,indispam,numspam = training(sys.argv[2]+'/spam/',stopset,0)

#======================test ==========================
    terms = []
    tempspam = []
    tempham = [] 
    tempspam = copy.copy(spamset)
    tempham = copy.copy(hamset)
    tempspam.extend(tempham)
    terms = list(set(tempspam))#get terms
    SUM = numspam + numham
    Pham = float(numham)/float(SUM)
    Pspam = float(numspam)/float(SUM)
    sumspam = len(terms) + indispam
    sumham = len(terms) + indiham

    ham1,spam1 = test(sys.argv[3]+'/ham/',hamset,spamset,hamVec,spamVec,sumham,sumspam)
    allF_ham = ham1 + spam1
    ham0,spam0 = test(sys.argv[3]+'/spam/',hamset,spamset,hamVec,spamVec,sumham,sumspam)
    allF_spam = ham0 + spam0
    # print 'spam rate = ' ,float(spam0)/float(allF_spam)
    # print 'ham rate = ' ,float(ham1)/float(allF_ham)
    f = open("results.txt", "w") 
    print 'spam rate = ' ,float(spam0)/float(allF_spam)
    print 'ham rate = ' ,float(ham1)/float(allF_ham)
    print 'accuracy rate =(with stopword)',  float(ham1 + spam0)/float(allF_ham + allF_spam)
    print >> f, 'accuracy rate =(with stopword)',  float(ham1 + spam0)/float(allF_ham + allF_spam)

    hamset,hamVec,indiham,numham = training(sys.argv[2] + '/ham/',stopset,1) 
    spamset,spamVec,indispam,numspam = training(sys.argv[2] + '/spam/',stopset,1)
    terms = []
    tempspam = []
    tempham = [] 
    tempspam = copy.copy(spamset)
    tempham = copy.copy(hamset)
    tempspam.extend(tempham)
    terms = list(set(tempspam))#get terms
    SUM = numspam + numham
    Pham = float(numham)/float(SUM)
    Pspam = float(numspam)/float(SUM)
    sumspam = len(terms) + indispam
    sumham = len(terms) + indiham

    ham1,spam1 = test(sys.argv[3] + '/ham/',hamset,spamset,hamVec,spamVec,sumham,sumspam)
    allF_ham = ham1 + spam1
    ham0,spam0 = test(sys.argv[3] + '/spam/',hamset,spamset,hamVec,spamVec,sumham,sumspam)
    allF_spam = ham0 + spam0
    print 'spam rate = ' ,float(spam0)/float(allF_spam)
    print 'ham rate = ' ,float(ham1)/float(allF_ham)
    print 'accuracy rate = (without stopword) ',  float(ham1 + spam0)/float(allF_ham + allF_spam)
    print >> f, 'accuracy rate =(without stopword)',  float(ham1 + spam0)/float(allF_ham + allF_spam)
    f.close()

