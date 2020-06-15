'''
Created on Jul 4, 2011

@author: Martin Vegi Kysel
'''

import math,re


def isprime(n):
    if n == 2:
        return 1
    if n % 2 == 0:
        return 0

    max = n**0.5+1
    i = 3
    
    while i <= max:
        if n % i == 0:
            return 0
        i+=2

    return 1

def getHorizontalSymmetry(s, booleanFlag =False, flexTileWidth = 0):
    '''
    @param s: list of values
    @return: ratio of symmetry [0,1]
    @summary: evaluates the horizontal symmetry of a matrix.
    '''
    
    axisSpecification =2
    if booleanFlag:
        axisSpecification = -1
    
    
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    overallError = 0.0
    for i in range(0,width):
        
        # select all columns and check if they are palindromes
        overallError+= getDifferenceInPalindromeString(s[i::width],axisSpecification)
        
    maxError = len(s)/2
    
    return 1-(overallError/maxError)
  
  
def getVerticalSymmetry(s , booleanFlag =False, flexTileWidth=0):  
    '''
    @param s: list of values
    @return: ratio of symmetry [0,1]
    @summary: evaluates the vertical symmetry of a matrix.
    '''
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    height = int(len(s)/width)
    
    axisSpecification =0
    if booleanFlag:
        axisSpecification = -1
    
    overallError = 0.0
    for i in range(0,height):
        
        # select all columns and check if they are palindromes
        overallError+= getDifferenceInPalindromeString(s[i*width:i*width+width],axisSpecification)
        
    maxError = len(s)/2

    return 1-(overallError/maxError)
  

def getFirstDiagonalSymmetry(s, booleanFlag =False):
    '''
    @param s: list of values
    @return: ratio of symmetry [0,1]
    @summary: evaluates the 1st diagonal symmetry of a matrix.
    '''
    LENGTH = math.sqrt(len(s))
    if LENGTH%1!=0.0:
        if isprime(len(s)):
            print("The array is of no possible matrix size")
            return -1
        else:
            print("Non-square matrix diagonal symmetry unspecified")
            return -1
    LENGTH = int(LENGTH)
    
    axisSpecification =1
    if booleanFlag:
        axisSpecification = -1
    
    overallError = 0.0
    # create a set of iterable numbers that identify diagonal lines in a matrix
    # select all positions in the first column and last row

    useThese = []
    useThese.extend(j for j in range(0,LENGTH))
    useThese.extend(j*LENGTH for j in range(1,LENGTH))
    for i in useThese:
        
        # this is a bit tricky
        # select every LENGTH+1'th element starting with i and do not select more elements,
        # that there should exist in one diagonal line
        overallError+= getDifferenceInPalindromeString(s[i::LENGTH+1][0:(LENGTH-int(i%LENGTH)-int(i/LENGTH))],axisSpecification)
        
    maxError = len(s)/2

    return 1-(overallError/maxError)

def getSecondDiagonalSymmetry(s, booleanFlag =False):
    '''
    @param s: list of values
    @return: ratio of symmetry [0,1]
    @summary: evaluates the 2nd diagonal symmetry of a matrix.
    '''
    
    LENGTH = math.sqrt(len(s))
    if LENGTH%1!=0.0:
        if isprime(len(s)):
            print("The array is of no possible matrix size")
            return -1
        else:
            print("Non-square matrix diagonal symmetry unspecified")
            return -1
    LENGTH = int(LENGTH)

    axisSpecification =3
    if booleanFlag:
        axisSpecification = -1

    overallError = 0.0
    
    # create a set of iterable numbers that identify 2nd diagonal lines in a matrix
    # select all numbers in the first row and last column
    useThese = []
    useThese.extend(j*LENGTH for j in range(1,LENGTH))
    useThese.extend(j for j in range(LENGTH*LENGTH-LENGTH+1,LENGTH*LENGTH-1))
    
    
   
    # select backwards every LENGTH'th element starting with i and do not select more elements,
    # that there should exist in one diagonal line
    for i in useThese:
        overallError+= getDifferenceInPalindromeString(s[i:0:-LENGTH+1][0:(int(i/LENGTH))+1-(i%LENGTH)],axisSpecification)
    
    maxError = len(s)/2

    return 1-(overallError/maxError)


def swap(x,pos1,pos2):
    '''
    @param x: string that has to be processed
    @param pos1,pos2: positions that identify the symbols in x to be swapped
    @summary: swaps characters at pos1 and pos2 in string x
    '''
    temp = x[pos1]
    x[pos1] = x[pos2]
    x[pos2] = temp


def rotate(x):
    '''
    @param x: input matrix
    @return: rotated matrix x
    @summary: rotates x by 90 degrees to the right. Should another angle be required, use this function multiple times.
    '''
    LENGTH = math.sqrt(len(x))
    if LENGTH%1!=0.0:
        #print LENGTH,"is not a square!"
        return -1
    LENGTH = int(LENGTH)
    
    
    # create a new matrix and fill it with values (these could also be 0)
    newArray = []
    for i in range(0,LENGTH*LENGTH):
        newArray.append(i)

    # iterate over the original matrix
    for i in range (0,LENGTH):
        for j in range (0,LENGTH):
            # set the values from the original matrix to a rotated position in the output matrix
            # always rotates by 90 degrees
            newArray[i*LENGTH+j]= x[(LENGTH-j-1)*LENGTH+i]
    
    return newArray

def angleAwareRotate(x):
    '''
    @param x: input matrix
    @return: adjusted matrix x
    @summary: rotates the values in the matrix by 90 degrees to the right. The position in the matrix remains the same.
    '''
    unawareX = rotate(x)
    if unawareX==-1:
        # rotation failed (not a square matrix)
        unawareX = x
    awareX = []
    for angle in unawareX:
        
        #check if the angle is actually a integer value. If not set it to 0 and print a warning.
        if not isAInteger(angle):
            print("angleAwareRotate WARNING:",angle, "is NaN")
            angle = 0
            
        awareX.append((angle+90)%360)
    return awareX

def isARotation(x,y):
    '''
    @param x: input matrix
    @param y: compared matrix
    @return: rotation between x and y;
            0 = 0
            1 = 90
            2 = 180
            3 = 270
    '''
    
    if len(x)!=len(y):
        print("isARotation ERROR: sizes do not match.")
        return -1
    
    # try 4 different rotations
    for i in range(0,4):
        
        # if they are equal return the representation of the orientation
        if x==y:
            return i
        
        # if they are not equal rotate the matrix to the right by 90 degrees
        x = angleAwareRotate(x)
        
    # no match found
    return -1 


def getOrientationCountsBy90Increment(s):
    '''
    @param s: input matrix
    @return: array of orientation sums [0,90,180,270]
    @summary: counts the block-orientations and groups them to 4 dominant parts
    '''
    zero = 0
    ninety = 0
    oeighty = 0
    twoseventy = 0
    
    for current in s:
        
        
        # set NaN values to 0
        if not isAFloat(current):
            print("getOrientationCountsBy90Inc ERROR:",current,"is NaN")
            current = 0
            
        
        if 315<current%360<=45:
            zero += 1
        
        elif 45<current%360<=135:
            ninety += 1
        
        elif 135<current%360<=225:
            oeighty += 1
        
        elif 225<current%360<= 315:
            twoseventy += 1
    
    return [zero,ninety,oeighty,twoseventy]
    

def isASpiral(s):
    '''
    @param s: input matrix
    @return: boolean decision for spiral-like categorization of s
    @summary: experimental function. Divides the matrix into 4 diagonal segments and counts the dominant orientation in the segment.
                If every segment has a different dominant orientation -> the matrix is spiral-like
    '''
    LENGTH = int(math.sqrt(len(s)))
    
    # we have 4 sectors with 4 possible item orientations
    sektors = []
    for i in range(0,4):
        appendable = [0 for i in range(0,4)]
        sektors.append(appendable)
    
    #iterate over the array
    position = 0
    for value in s:
        
        # compute a position i/j in the matrix
        i = int(position/LENGTH)
        j = int(position%LENGTH)
        
        # find the appropriate section for each item and increase the counter for the found item
        
        
        # top sector
        if j-i>=0 and i+j<=LENGTH-1:
            sektors[0][value-1]+= 1
        
        # left sector    
        if j-i<=0 and i+j<=LENGTH-1:
            sektors[3][value-1]+=1
        
        # right sector
        if j-i>=0 and i+j>=LENGTH-1:
            sektors[1][value-1]+=1
        
        #bottom sector    
        if j-i<=0 and i+j>=LENGTH-1:
            sektors[2][value-1]+=1
            
        position+=1
    
    # each sector should have its signature item orientation
    # if this is not the case, the matrix is not spiral-like
    # there must be no order of occurrence in the sectors
    # one signature item can not occur in more than 1 sector
    overflow = 0
    
    
    # -1 if the item orientation is in no sector the dominant one
    maxSectorsAlreadyFound = [-1 for i in range(0,LENGTH)]
    
    
    # iterate over all sectors
    for i in range(0,LENGTH):
        
        # find the maximal sum of items
        max = sorted(sektors[i])[::-1][0]
        
        for j in range(0,len(sektors[i])):
            
            # iterate over all items in a sector, if it is the maximum write it into the alreadyFoundArray
            # if the array is already set, the item cannot be a signature item for this sector and the algorithm closes
            # the maximal value must also be above the expected value of 1/4th
            # both diagonals are counted in both according sectors and the middle is in all 4 sectors
            # therefore this condition should be manageable
            if sektors[i][j] == max and sektors[i][j]>=(len(s)/4):
                if maxSectorsAlreadyFound[j]==-1:
                    maxSectorsAlreadyFound[j]= i
                else:
                    overflow=1
                    break
            elif sektors[i][j] == max and sektors[i][j]<(len(s)/4):
                overflow=1
                break
        
        # break from the section loop    
        if overflow==1:
            break
    
    # if sector has its signature and every signature should be located only in one sector
    # then the matrix is spiral-like
    if overflow==0:
        return 1
    return 0

              
def drawMatrix(s,flexTileWidth=0):
    '''
    @param s: input matrix
    @return: list of lines to be printed on the result file
    @summary: draws a representation of the matrix. Assumes hor/ver orientation of blocks.
    '''
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    
    
    # specifies a line of the matrix. A \n characted could be appended instead
    stringBuffer = ""
    outList = []
    
    for current in s:
        if current==0:
            stringBuffer+="^"
        elif current==90:
            stringBuffer+=">"
        elif current==180:
            stringBuffer+="v"
        elif current==270:
            stringBuffer+="<"
        
        # print the line, start filling the next
        if len(stringBuffer)==width:
            outList.append(stringBuffer)
            stringBuffer = ""
    return outList
              
def drawBWMatrix(s,flexTileWidth=0):
    '''
    @param s: input matrix
    @return: list of lines to be printed on the result file
    @summary: draws a representation of a black and white matrix. 
    '''
    
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    
    
    # specifies a line of the matrix. A \n character could be appended instead
    stringBuffer = ""
    outList = []
    
    for current in s:
        if current==0:
            stringBuffer+="X"
        else:
            stringBuffer+="O"
        
        # print the line, start filling the next
        if len(stringBuffer)==width:
            outList.append(stringBuffer)
            stringBuffer = ""
    return outList
            
            
def getSymmetryValues(s, binaryFlag = False, flexTileWidth = 0):
    '''
    @param s: input matrix
    @param binaryFlag: identifies a black-white/binary matrix, no angle aware invertion
    @return: an array of symmetries
            [0]: horizontal
            [1]: vertical
            [2]: 1st diagonal
            [3]: 2nd diagonal
    '''
    values = []
    values.append(getHorizontalSymmetry(s,binaryFlag,flexTileWidth))
    values.append(getVerticalSymmetry(s,binaryFlag,flexTileWidth))
    values.append(getFirstDiagonalSymmetry(s,binaryFlag))
    values.append(getSecondDiagonalSymmetry(s,binaryFlag))
    
    return values


def getTileMakerSymmetry(s, binaryFlag = False,flexTileWidth=0):
    '''
    @param s: input matrix in string format
    @param binaryFlag: currently unsupported
    @return: ratio of tile makers symmetry
    @summary: selects the best possible match for a tile makers symmetry. Only perfect matches are counted.
                The default matrix starts with a 0 orientation in the top left corner and continues to grow clockwise. Rotations of this matrix are also tested.
    '''
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    height = int(len(s)/width)
    
    # default tilemaker matrix and its rotations
    #     0     90
    #     270   180
    
    defaultsByOffset = [0 for i in range (0,4)]
    defaultsByOffset[0] = [[0,90],[270,180]] # default
    defaultsByOffset[1] = [[270,0],[180,90]] # 90 degrees to the left
    defaultsByOffset[2] = [[180,270],[90,0]] # 180 degrees to the left
    defaultsByOffset[3] = [[90,180],[0,270]] # 270 degrees to the left
    
    
    # the maximal number of possible matches. Half and quarter finds possible
    maxFinds = (width/2.0)*(height/2.0)
    
    # 4 orientations are tested and the best is selected.
    bestFind = 0.0
    
    # iterate over the orientations
    for i in range (0,4):
            
        # select the next
        tileMakersDefault = defaultsByOffset[i]
        
        finds = 0.0
        
        
        # this algorithm is rather simple and uses no types of padding
        # the matrix is divided into full matches, half matches and quarter matches
            # full matches are inside the matrix
            # half matches are at the boundaries of the matrix
            # quarter matches consist of a single element at the corner
        
        # select every element in the matrix starting with the first up to a maximum of LENGTH-1
        # the last element is not selected in this procedure as no full match can be found
        for i in range (0,height-1):
            for j in range (0, width-1):
                # submatrix starts with i/j and is of size 2x2.
                currentSubMatrix = [[s[k*width+l] for l in range(j,j+2)] for k in range(i,i+2)]
            
                # only exact! matches are counted.
                if currentSubMatrix == tileMakersDefault:
                    finds += 1
                    
        
        # search for half-finds at the boundaries
        
        # 1st row, procedure is common for others
        # iterate over the first row, stop with the last-1
        for j in range(0,width-1):
            # select a submatrix at position [0][j] of size 1x2
            currentSubMatrix= [s[0+l] for l in range(j,j+2)]
            # if the 2x1 submatrix matches the last row of the predifined matrix a half match is found
            if currentSubMatrix == tileMakersDefault[1]:
                finds += 0.5
           
        # last row
        for j in range(0,width-1):
            currentSubMatrix= [s[width*(height-1)+l] for l in range(j,j+2)]
            if currentSubMatrix == tileMakersDefault[0]:
                finds += 0.5
        
        # 1st column
        for i in range(0,height-1):
            currentSubMatrix= [s[width*k] for k in range(i,i+2)]
            if currentSubMatrix == [tileMakersDefault[k][1] for k in range(0,2)]:
                finds += 0.5
        # last column
        for i in range(0,height-1):
            currentSubMatrix= [s[width*k+width-1] for k in range(i,i+2)]
            if currentSubMatrix == [tileMakersDefault[k][0] for k in range(0,2)]:
                finds += 0.5
        
        # 3rd search iteration, just the edges
        
        # top left corner must match the bottom right element of the default matrix
        # if so, a quarter match is found
        if s[0] == tileMakersDefault[1][1]:
            finds+= 0.25
        # top right   
        if s[width-1] == tileMakersDefault[1][0]:
            finds += 0.25
        # bottom left    
        if s[width* height - width] == tileMakersDefault[0][1]:
            finds += 0.25
        # bottom right    
        if s[width*height -1] == tileMakersDefault[0][0]:
            finds += 0.25
    
        # select the best orientation of the default tile makers matrix
        if finds>bestFind:
            bestFind = finds
            
    # the best orientation is selected and divided by the number of maximal matches
    return bestFind/maxFinds
    

def getRotationalSymmetries(s, binaryFlag =False, flexTileWidth=0):
    '''
    @param s: input matrix
    @return: array of rotational symmetries
    @summary: first value is a 2x1 or 1x2 matrix division. Those are equivalent.
                Second value is a 2x2 matrix division.
                The ratio of rotational symmetry is returned.
                1 for perfect rotational symmetry
                0 for a perfectly random matrix
    '''
    values =[]
    
    isSquare = 1
    if math.sqrt(len(s))%1!=0.0:
        isSquare = 0
        
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    
    # get 4 separate parts of the matrix
    # if the matrix has an odd number of rows, fill additional 4 lists representing the middle rows/columns
    submatrices = divideMatrixIntoTwoTimesTwo(s,width)
    
    #2x1 division equals 1x2
    ratio2 = 0.0
    ratio2+= getRatioOfEquivalenceByRotation(submatrices[0],submatrices[3], 180, binaryFlag)
    ratio2+= getRatioOfEquivalenceByRotation(submatrices[1],submatrices[2], 180, binaryFlag)
    values.append(ratio2/2)
    
    #2x2 division
    if isSquare:
        ratio4 = 0.0
        ratio4+= ratio2
    
        ratio4+= getRatioOfEquivalenceByRotation(submatrices[0],submatrices[1], 90, binaryFlag)
        ratio4+= getRatioOfEquivalenceByRotation(submatrices[1],submatrices[3], 90, binaryFlag)
        ratio4+= getRatioOfEquivalenceByRotation(submatrices[3],submatrices[2], 90, binaryFlag)
        ratio4+= getRatioOfEquivalenceByRotation(submatrices[2],submatrices[0], 90, binaryFlag)
        
        nrComparisons = 6
        
        # if the number of rows/columns is odd 4 extra values are returned by the divide2x2 procedure
        # therefore the (5th) value wont be 0
        if len(submatrices[4])!=0:
            
            # impact is based on the size of the matrix. The middle row or column has less values than the full submatrix
            # a 3x3 matrix has an equal number of values in the middle and in the submatrix
            # a 5x5 matrix has 2x more values in the submatrix
            # divide the ratio of the find by the impart ratio
            impact = 1.0/(LENGTH/2)
            print("impact",impact)
            
            # lower the importance of the finding by the ratio of impact
            ratio4+= impact*getRatioOfEquivalenceByRotation(submatrices[4],submatrices[5], 90, binaryFlag)
            ratio4+= impact*getRatioOfEquivalenceByRotation(submatrices[5],submatrices[6], 90, binaryFlag)
            ratio4+= impact*getRatioOfEquivalenceByRotation(submatrices[6],submatrices[7], 90, binaryFlag)
            ratio4+= impact*getRatioOfEquivalenceByRotation(submatrices[7],submatrices[4], 90, binaryFlag)
            ratio4+= impact*getRatioOfEquivalenceByRotation(submatrices[4],submatrices[6], 180, binaryFlag)
            ratio4+= impact*getRatioOfEquivalenceByRotation(submatrices[5],submatrices[7], 180, binaryFlag)
            
            # the final nrComparisons will be 6 + impact*6
            # a 3x3 matrix will have 12 comparisons
            # a 5x5 matrix will have only 9 (the additional odd rows will have a half impact)
            nrComparisons+= 6*impact
        
        values.append(ratio4/nrComparisons)
    else:
        # non-squre matrices have unspecified 2x2 rotation
        values.append(-1)
    
    return values

def getRatioOfEquivalenceByRotation(x,y,rotation, binaryFlag = False):
    '''
    @param x: input matrix
    @param y: compared matrix
    @param rotation: rotation offset of matrix y
    @return: sum of difference between matrices
    @summary: rotates matrix y based on rotation and compares it to x
    '''
    
    if len(x)!=len(y):
        print("gROEBR: sizes must match!")
        return -1
     
    if not isAInteger(rotation):
        print("gROEbR ERROR:",rotation,"is not a valid rotation value")
    else:
        rotation = int(rotation)
        
    isSquare = 1
    if math.sqrt(len(x))%1!=0.0:
        isSquare = 0
    
    rotation = int(rotation/90) + rotation%90 # both 90 and 1 will become the same number
    
    
    # rotate the square positions themselves
    if isSquare and rotation==1:
        x = rotate(x)
    elif rotation==2:
        x = x[::-1]
    elif isSquare and rotation==1:
        x = x[::-1]
        x = rotate(x)
        
    # rotate the values
    for _ in range(0,rotation):
        if not binaryFlag:
            x = angleAwareRotate(x)

    error = 0.0    
    for position in range(0,len(x)):
        if x[position]!=y[position]:
            error +=1
    return 1 - (error/len(x))

def divideMatrixIntoTwoTimesTwo(s,flexTileWidth=0):
    '''
    @param s: input matrix
    @return: array of sub-matrices
    @summary: divides the input matrix into four equal sub-parts
    @summary: parts are as follows: top left, top right, bottom left, bottom right
    '''
    if flexTileWidth ==0:
        
        LENGTH = math.sqrt(len(s))
        if LENGTH%1!=0.0:
            print("FlexTileWidth unspecified. Cannot continue!")
            return -1
        else:
            # unspecified width, computes itself
            width = int(LENGTH)
            
    elif isprime(len(s)):
        print("The array is of no possible matrix size")
        return -1
    else:
        width = flexTileWidth
    
    height = int(len(s)/width)
    # check if the matrix has an even number of rows/columns
    # in case of odd number, start an extra procedure for the middle row/column, ignore the true middle
    unevenOffset = 0
    if width%2==1:
        unevenOffset= 1
    
    lT = [] # left top
    lB = [] # left bottom
    rT = [] # right top
    rB = [] # right bottom
    mT =[] # middle top
    mR = [] # middle right
    mL = [] # middle left
    mB = [] # middle bottom
    
    # iterate over the matrix string
    for position in range(0,len(s)):
        row = position/width
        column = position%width
        
        # append the value to its appropriate list
        if row <height/2 and column <width/2:
            lT.append(s[position])
        elif row <height/2 and column >=width/2+unevenOffset:
            rT.append(s[position])
        elif row >=height/2+unevenOffset and column <width/2:
            lB.append(s[position])
        elif row >=height/2+unevenOffset and column >=width/2+unevenOffset:
            rB.append(s[position])
        
        # create extra lists for the middle values
        if unevenOffset>0:
            if row == height/2 and column<width/2:
                mL.append(s[position])
            if row == height/2 and column>width/2:
                mR.append(s[position])
            if row < height/2 and column ==width/2:
                mT.append(s[position])
            if row > height/2 and column ==width/2:
                mB.append(s[position])
                      
        
    
    return [lT,rT,lB,rB,mT,mR,mB,mL]

def isPalindrome(s, axis=-1):
    half = len(s)/2

    part1 = s[0:half]
    part2 = s[(len(s)-half):len(s)][::-1]
    
    if not isAInteger(axis):
        axis = -1
    else:
        axis = int(axis)
    
    if axis>=0:
        #print "axis specified",axis
        part2 = invertByAxis(part2,axis)
    
    if part1==part2:
        return 1
    return 0

def getDifferenceInPalindromeString(s, axis=-1):
    '''
    @param s: input matrix line
    @param axis: tested axis of symmetry
    @return: difference to perfect palindrome, 0 indicates no difference
    @summary: separates the line into half, inverts the other one based on axis and returns the difference

    '''
    # make sure the axis definition is valid
    if not isAInteger(axis):
        axis = -1    
    else:
        axis = int(axis)
    
    
    # divide the matrix line into two halves, ignoring the middle element
    # invert the second
    half = int(len(s)/2)

    part1 = s[0:half]
    part2 = s[(len(s)-half):len(s)][::-1]
    
    
    # invert the values of the second part based on axis definition
    # do not perform an invertion if axis = -1
    if axis>=0:
        part2 = invertByAxis(part2,axis)
    
    # count the error
    errorSum = 0
    for i in range(0,len(part1)):
        if part1[i]!=part2[i]:
            errorSum+= 1
    return errorSum

def invertByAxis(s,axis):
    '''
    @param s: the matrix to be inverted
    @param axis: axis of rotation
    @return: inverted matrix s
    @summary: inverts all rotation-aware orientations based on the axis specified
    
    # axis definition:
    # 0 vertical
    # 2 horizontal
    # 1 1st diagonal
    # 3 2nd diagonal
    '''
    
    # make sure the axis value is valid
    if (not isAInteger(axis)):
        print("invertByAxis ValueError: axis not specified correctly")
        return -1
    
    axis = int(axis)
    
    if (axis<0):
        print("invertByAxis ValueError: negative axis value, are you using the function right?")
        return -1
    
    newS =[]
    for x in s:
        # make no changes on non-integers
        if not isAInteger(x):
            newS.append(x)
            continue
        
        newx = 0
        if axis%4==0:
            newx = (90-x)%360
        if axis%4==2:
            newx = (270-x)%360
        if axis%4==1:
            newx = (180-x)%360
        if axis%4==3:
            newx = (-x)%360
        newS.append(newx)
        
    return newS

def Entropy(x):
    '''
    @param x: array of probabilities
    @return: Entropy value in bits 
    @summary: Shannon Entropy - S =  - [SUM] P(i) ln P(i)
    '''
    
    S = 0.0
     
    for current in x:
        
        if not isAFloat(current):
            print("Entropy Function Error:",current, "is not a number.")
            continue
        else:
            current = float(current)
            
        # log(2) of 0 is not defined!
        if current!=0:
            value = current * math.log(current,2)
            S+= value
    
    
    # return absolute summary
    return math.fabs(-S)
    
def extractNonDigitPrefix(digitPositionString):
    '''
    @summary: returns the prefix of the input separated by the first digit, ignores file type
    @param string: input
    @return: substring 
    '''
    
    # take only the part before "." = ignore file type
    digitPositionString = digitPositionString.partition(".")[0]
    
    strLen = len(digitPositionString)
    firstPosition = 0
    
    # use a inverted range strLen:0
    for i in range (strLen):
        
        #get the symbol at the position starting from the end
        value =  digitPositionString[strLen-i-1]
        
        # first nonDigit value breaks the loop
        if not str.isdigit(value):
            
            # save the position of the last digit
            firstPosition = strLen-i
            break
        
    # return the substring 0 to the first digit(exclusive)
    return digitPositionString[0:firstPosition]

def trimAllWhitespace(s):
    '''
    @param s: string with whitespace
    @return: input strings with whitespace removed
    @summary: Trims all whitespace from the input string
    '''
    pat = re.compile(r'\s+')
    return pat.sub('', s)

def findAll(s,symbol):
    '''
    @param s: input string
    @param symbol: character/string to be found 
    @return: list of positions of the symbol
    @summary: Finds the position of all occurrences of char symbol in string s
    '''
    return [match.start() for match in re.finditer(re.escape(symbol), s)]


def printRoundedArray(x):
    '''
    @param x: array of values 
    @return: none
    @summary: prints rounded values to three decimal spaces
    '''
    try:
        for current in x:
            print("%.3f" % current)
    except TypeError:
            print(x)

def roundArray(x, places):
    '''
    @param x: array of values
    @param places: number of decimal places
    @return: rounded array to _places_ decimal places
    @bug: depends on python version
    '''
    returnArray = []
    try:
        for current in x:
            value = round(current,3)
            returnArray.append(value)
        return returnArray
    except TypeError:
        print("just one value delivered")
        return [round(x,3)]
    

def isAFloat(s):
    '''
    @param s: string to be tested
    @return: boolean decision
    @summary: tests if a string is a float, 
                does not work simple isDigit() because decimal numbers are categorized wrongly 
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def isAInteger(s):
    '''
    @param s: string to be tested
    @return: boolean decision
    @summary: tests if a string is a integer, 
                does not work simple isDigit() because decimal numbers are categorized wrongly 
    '''
    try:
        int(s)
        return True
    except ValueError:
        return False
