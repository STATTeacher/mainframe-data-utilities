# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# FUNCTIONS TO HANDLE THE HIERARCHICAL STACK #
def fGetSetack():
    global stack, output
    tmp = output
    for k in stack:
        tmp = tmp[stack[k]]
    return tmp

def fRemStack(iStack,iLevel):
    NewStack = {}
    for k in iStack:
        if k < iLevel: NewStack[k] = iStack[k]
    return NewStack

#PIC 999, 9(3), XXX, X(3)...
def getPicSize(arg):
    if arg.find("(") > 0: 
        return int(arg[arg.find("(")+1:arg.find(")")])
    else:
        return len(arg)

# TYPE AND LENGTH CALCULATION #
def getLenType(atr):
    ret = {}
    FirstCh = atr[3][:1].upper()
    Picture = atr[3].upper()

    #data type
    if   'COMP-3'in atr and FirstCh=='S': ret['type'] = "pd+"
    elif 'COMP-3'in atr:                  ret['type'] = "pd"
    elif 'COMP'  in atr and FirstCh=='S': ret['type'] = "bi+"
    elif 'COMP'  in atr:                  ret['type'] = "bi"
    elif FirstCh=='S':                    ret['type'] = "zd+"
    elif FirstCh=='9':                    ret['type'] = "zd"
    else:                                 ret['type'] = "ch"

    #Total data length
    PicNum = Picture.replace("V"," ").replace("S","").replace("-","").split()
    
    Lgt = getPicSize(PicNum[0])

    if len(PicNum) == 1:
        ret['dplaces'] = 0
    else:
        ret['dplaces'] = getPicSize(PicNum[1])
        Lgt += ret['dplaces']

    ret['length'] = Lgt

    #Data size in bytes
    if   ret['type'][:2] == "pd": ret['bytes'] = round((Lgt/2))+1
    elif ret['type'][:2] == "bi": 
        if   Lgt <  5:             ret['bytes'] = 2
        elif Lgt < 10:             ret['bytes'] = 4
        else         :             ret['bytes'] = 8
    else:                          
        if FirstCh=='-': Lgt += 1
        ret['bytes'] = Lgt
        
    return ret

############# DICTIONARY AND HIERARCHICAL LOGIC ###########################
def add2dict(lvl, grp, itm, stt, id):

    global cur, output, last, stack, FillerCount

    if itm.upper() == "FILLER":
        FillerCount += 1
        itm = itm + "_" + str(FillerCount)

    if lvl <= cur: stack = fRemStack(stack, lvl)

    stk = fGetSetack()
    stk[itm]= {}
    stk[itm]['id'] = id
    stk[itm]['level'] = lvl
    stk[itm]['group'] = grp
    if 'OCCURS'   in stt: stk[itm]['occurs']    = int(stt[stt.index('OCCURS')+1])
    if 'REDEFINES'in stt: stk[itm]['redefines'] = stt[stt.index('REDEFINES')+1]

    if grp == True:
        stack[lvl] = itm
        cur = lvl
    else:
        tplen = {}
        tplen = getLenType(stt)
        stk[itm]['pict'] = stt[3]
        stk[itm]['type'] = tplen['type']
        stk[itm]['length'] = tplen['length']
        stk[itm]['bytes'] = tplen['bytes']
        stk[itm]['dplaces'] = tplen['dplaces']

############################### MAIN ###################################
# READS, CLEANS AND JOINS LINES #

FillerCount=0
cur=0
output={}
stack = {}

def toDict(lines):

    id = 0
    stt = ""
    for line in lines: 
        if len(line) > 1:
            if line[6] != "*": stt += line.replace('\t', '    ')[6:72]    

    # READS FIELD BY FIELD / SPLITS ATTRIBUTES #
    for variable in stt.split("."):
        
        attribute=variable.split()

        if len(attribute) > 0:
            if attribute[0] != '88': 
                id += 1
                add2dict(int(attribute[0]), False if 'PIC'in attribute else True, attribute[1], attribute, id)

    return output