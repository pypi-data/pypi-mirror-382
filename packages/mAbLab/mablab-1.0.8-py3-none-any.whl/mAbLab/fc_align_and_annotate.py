from Bio import Align
from Bio.Seq import Seq

def load_and_parse_reference_data():
    """
    Loads the reference data from the specified and constructs reference sequences and annotation tables for each IgG isotype.

    Returns:
        A tuple containing two dictionaries:
        - ref_sequences: {'IgG1': Seq(...), 'IgG2': Seq(...), ...}
        - ref_annotations: {'IgG1': [...], 'IgG2': [...], ...}
    """
    data = {
        'index':"[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500]",

        'aa':"[-,-,-,-,A,S,T,K,G,P,S,V,F,P,L,A,P,S,S,K,S,T,S,-,-,-,G,G,T,A,A,L,G,C,L,V,K,D,Y,F,P,-,-,E,P,V,T,V,S,W,N,S,G,A,L,T,S,-,-,-,-,G,V,H,T,F,P,A,V,L,Q,S,S,-,-,-,-,-,-,G,L,Y,S,L,S,S,V,V,T,V,P,S,S,S,L,-,-,-,G,T,Q,T,Y,I,C,N,V,N,H,K,P,-,-,S,N,T,K,V,D,K,K,V,-,-,-,-,-,-,-,-,-,E,P,K,S,C,D,K,T,H,T,C,P,P,C,P,(E),R,K,C,C,V,E,C,P,P,C,P,(E),L,K,T,P,L,G,D,T,T,H,T,C,P,R,C,P,(E),P,K,S,C,D,T,P,P,P,C,P,R,C,P,-,-,(E),P,K,S,C,D,T,P,P,P,C,P,R,C,P,-,-,(E),P,K,S,C,D,T,P,P,P,C,P,R,C,P,-,-,(E),S,K,Y,G,P,P,C,P,S,C,P,-,-,A,P,E,L,L,G,G,P,S,V,F,L,F,P,P,K,P,K,D,T,L,M,I,-,S,R,T,P,E,V,T,C,V,V,V,D,V,S,H,E,D,P,E,V,K,F,N,W,Y,V,D,G,V,E,V,H,-,-,-,N,A,K,T,K,P,R,E,E,Q,Y,N,-,-,-,-,-,-,S,T,Y,R,V,V,S,V,L,T,V,L,H,Q,D,W,-,-,L,N,G,K,E,Y,K,C,K,V,S,N,K,A,-,-,L,P,A,P,I,E,K,T,I,S,K,A,K,-,-,-,-,-,-,-,-,-,G,Q,P,R,E,P,Q,V,Y,T,L,P,P,S,R,D,E,L,T,-,-,-,K,N,Q,V,S,L,T,C,L,V,K,G,F,Y,P,-,-,S,D,I,A,V,E,W,E,S,N,G,Q,P,E,N,-,-,-,N,Y,K,T,T,P,P,V,L,D,S,D,-,-,-,-,-,-,G,S,F,F,L,Y,S,K,L,T,V,D,K,S,R,W,-,-,Q,Q,G,N,V,F,S,C,S,V,M,H,E,A,-,L,H,N,H,Y,T,Q,K,S,L,S,L,S,P,-,-,-,G,K]",

        'domain':"[CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,CH1,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG1-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG2-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG3-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,IgG4-hinge,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH2,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3,CH3]",

        'structure':"[-,-,-,-,-,-,-,-,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,AB-TURN,AB-TURN,AB-TURN,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,EF-TURN,EF-TURN,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,AB-TURN,AB-TURN,AB-TURN,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,EF-TURN,EF-TURN,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,-,-,-,-,-,-,-,-,-,-,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,A-STRAND,AB-TURN,AB-TURN,AB-TURN,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,B-STRAND,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,BC-LOOP,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,C-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,CD-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,D-STRAND,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,DE-TURN,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,E-STRAND,EF-TURN,EF-TURN,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,F-STRAND,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,FG-LOOP,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,G-STRAND,-,-]",

        'imgt_unique':"[1.8,1.7,1.6,1.5,1.4,1.3,1.2,1.1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15.1,15.2,15.3,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,34,35,36,37,38,39,40,41,42,43,44,45,45.1,45.2,45.3,45.4,45.5,45.6,45.7,77,78,79,80,81,82,83,84,84.1,84.2,84.3,84.4,84.5,84.6,84.7,85.7,85.6,85.5,85.4,85.3,85.2,85.1,85,86,87,88,89,90,91,92,93,94,95,96,96.1,96.2,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,1,2,3,4,5,6,7,8,9,10,11,12,1.8,1.7,1.6,1.5,1.4,1.3,1.2,1.1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15.1,15.2,15.3,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,34,35,36,37,38,39,40,41,42,43,44,45,45.1,45.2,45.3,45.4,45.5,45.6,45.7,77,78,79,80,81,82,83,84,84.1,84.2,84.3,84.4,84.5,84.6,84.7,85.7,85.6,85.5,85.4,85.3,85.2,85.1,85,86,87,88,89,90,91,92,93,94,95,96,96.1,96.2,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,1.8,1.7,1.6,1.5,1.4,1.3,1.2,1.1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15.1,15.2,15.3,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,34,35,36,37,38,39,40,41,42,43,44,45,45.1,45.2,45.3,45.4,45.5,45.6,45.7,77,78,79,80,81,82,83,84,84.1,84.2,84.3,84.4,84.5,84.6,84.7,85.7,85.6,85.5,85.4,85.3,85.2,85.1,85,86,87,88,89,90,91,92,93,94,95,96,96.1,96.2,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130]",

        'imgt':"[-,-,-,-,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,-,-,-,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,-,-,35,36,37,38,39,40,41,42,43,44,45,46,47,48,-,-,-,-,49,50,51,52,53,54,55,56,57,58,59,60,-,-,-,-,-,-,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,-,-,-,77,78,79,80,81,82,83,84,85,86,87,88,89,-,-,90,91,92,93,94,95,96,97,98,-,-,-,-,-,-,-,-,-,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,-,-,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,-,-,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,-,-,1,2,3,4,5,6,7,8,9,10,11,12,-,-,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,-,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,-,-,-,56,57,58,59,60,61,62,63,64,65,66,67,-,-,-,-,-,-,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,-,-,84,85,86,87,88,89,90,91,92,93,94,95,96,97,-,-,98,99,100,101,102,103,104,105,106,107,108,109,110,-,-,-,-,-,-,-,-,-,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,-,-,-,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,-,-,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,-,-,-,50,51,52,53,54,55,56,57,58,59,60,61,-,-,-,-,-,-,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,-,-,78,79,80,81,82,83,84,85,86,87,88,89,90,91,-,92,93,94,95,96,97,98,99,100,101,102,103,104,105,-,-,-,CHS 106,CHS 107]",

        'kabat':"[-,-,-,-,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,133,134,-,-,-,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,-,-,150,151,152,153,154,156,157,162,163,164,165,166,167,168,-,-,-,-,169,171,172,173,174,175,176,177,178,179,180,182,-,-,-,-,-,-,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,-,-,-,199,200,203,205,206,207,208,209,210,211,212,213,214,-,-,215,216,217,218,219,220,221,222,223,-,-,-,-,-,-,-,-,-,226,227,228,232,233,234,235,236,237,238,239,240,241,242,243,226,227,228,232,233,235,237,239,240,241,242,243,226,227,228,229,230,232,233,234,235,236,237,238,239,240,241,241A,241B,241C,241D,241E,241F,241G,241H,241I,241J,241K,241L,241M,241N,241O,241P,241Q,-,-,241R,241S,241T,241U,241V,241W,241X,241Y,241Z,241AA,241BB,241CC,241DD,241EE,241FF,-,-,241GG,241HH,241II,241JJ,241KK,241LL,241MM,241NN,241OO,241PP,241QQ,241RR,241SS,242,243,-,-,226,227,228,229,230,237,238,239,240,241,242,243,-,-,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,-,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,295,296,299,300,301,302,-,-,-,303,304,305,306,307,308,309,310,311,312,313,314,-,-,-,-,-,-,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,-,-,333,334,335,336,337,338,339,340,341,342,343,344,345,346,-,-,347,348,349,350,351,352,353,354,355,357,358,359,360,-,-,-,-,-,-,-,-,-,361,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,381,382,-,-,-,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,-,-,398,399,400,401,402,405,406,407,408,410,411,414,415,416,417,-,-,-,418,419,420,421,422,423,424,425,426,427,428,430,-,-,-,-,-,-,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,-,-,449,450,451,452,453,454,455,456,457,458,459,460,461,462,-,463,464,465,466,467,468,469,470,471,472,473,474,475,476,-,-,-,477,478]",

        'eu':"[-,-,-,-,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,-,-,-,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,-,-,152,153,154,155,156,157,158,159,160,161,162,163,164,165,-,-,-,-,166,167,168,169,170,171,172,173,174,175,176,177,-,-,-,-,-,-,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,-,-,-,194,195,196,197,198,199,200,201,202,203,204,205,206,-,-,207,208,209,210,211,212,213,214,215,-,-,-,-,-,-,-,-,-,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,216,217,218,219,220,222,224,226,227,228,229,230,216,217,218,-,-,219,220,221,222,223,224,225,226,227,228,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,229,230,-,-,216,217,218,-,-,224,225,226,227,228,229,230,-,-,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,-,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,-,-,-,286,287,288,289,290,291,292,293,294,295,296,297,-,-,-,-,-,-,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,-,-,314,315,316,317,318,319,320,321,322,323,324,325,326,327,-,-,328,329,330,331,332,333,334,335,336,337,338,339,340,-,-,-,-,-,-,-,-,-,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,-,-,-,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,-,-,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,-,-,-,390,391,392,393,394,395,396,397,398,399,400,401,-,-,-,-,-,-,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,-,-,418,419,420,421,422,423,424,425,426,427,428,429,430,431,-,432,433,434,435,436,437,438,439,440,441,442,443,444,445,-,-,-,446,447]"
        }
    
    data = {key: value.strip('[]').split(',') for key, value in data.items()}

    ref_sequences = {'IgG1': '', 'IgG2': '', 'IgG3': '', 'IgG4': ''}
    ref_annotations = {'IgG1': [], 'IgG2': [], 'IgG3': [], 'IgG4': []}

    # Construct sequences and annotation tables for each isotype
    for i in range(len(data['index'])):
        aa = data['aa'][i]
        domain = data['domain'][i]
        
        # Skip placeholder entries
        if aa == '-':
            continue

        annotation_entry = (
            data['index'][i],
            data['eu'][i],
            data['kabat'][i],
            data['imgt_unique'][i],
            data['imgt'][i],
            domain,
            data['structure'][i]
        )

        if 'IgG1' in domain or domain in ['CH1', 'CH2', 'CH3']:
            ref_sequences['IgG1'] += aa
            ref_annotations['IgG1'].append(annotation_entry)
        if 'IgG2' in domain or domain in ['CH1', 'CH2', 'CH3']:
            ref_sequences['IgG2'] += aa
            ref_annotations['IgG2'].append(annotation_entry)
        if 'IgG3' in domain or domain in ['CH1', 'CH2', 'CH3']:
            ref_sequences['IgG3'] += aa
            ref_annotations['IgG3'].append(annotation_entry)
        if 'IgG4' in domain or domain in ['CH1', 'CH2', 'CH3']:
            ref_sequences['IgG4'] += aa
            ref_annotations['IgG4'].append(annotation_entry)

    # Convert sequence strings to Biopython Seq objects
    for isotype in ref_sequences:
        ref_sequences[isotype] = Seq(ref_sequences[isotype])

    return ref_sequences, ref_annotations

def analyze_heavy_chain(sequence, ref_sequences, ref_annotations):
    """
    Analyzes an antibody heavy chain sequence using the loaded reference data.
    """
    # Find the start of the constant region to align properly
    c_region_start = sequence.find("ASTKGPS")
    c_region_start_display = 0 if c_region_start == -1 else c_region_start
    input_seq_str = sequence[c_region_start_display:]
    input_seq = Seq(input_seq_str)

    # Identify the best matching isotype by alignment score
    isotype = None
    best_score = -1
    aligner = Align.PairwiseAligner()
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -0.5
    aligner.extend_gap_score = -0.1

    for isotype, ref_seq in ref_sequences.items():
        if not ref_seq:
            continue
        # Use PairwiseAligner for a more sensitive alignment score
        alignments = aligner.align(str(input_seq), str(ref_seq))
        if alignments and alignments[0].score > best_score:
            best_score = alignments[0].score
            best_isotype = isotype

    if not best_isotype:
        return None, []

    # Perform the final, detailed alignment against the best-matched reference
    ref_seq = ref_sequences[best_isotype]
    aligner.match_score = 5
    aligner.mismatch_score = -4
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    alignment = aligner.align(str(input_seq), str(ref_seq))[0]
    aligned_input = alignment.aligned[0]
    aligned_ref = alignment.aligned[1]

    # Reconstruct aligned sequences as strings
    def reconstruct_alignment(seq, aligned_spans):
        result = []
        last = 0
        for start, end in aligned_spans:
            # Add gaps if needed
            if start > last:
                result.extend(['-'] * (start - last))
            result.extend(list(seq[start:end]))
            last = end
        # Add trailing gaps if needed
        if last < len(seq):
            result.extend(['-'] * (len(seq) - last))
        return result

    aligned_input_str = reconstruct_alignment(str(input_seq), aligned_input)
    aligned_ref_str = reconstruct_alignment(str(ref_seq), aligned_ref)
    # Pad to equal length
    max_len = max(len(aligned_input_str), len(aligned_ref_str))
    aligned_input_str += ['-'] * (max_len - len(aligned_input_str))
    aligned_ref_str += ['-'] * (max_len - len(aligned_ref_str))

    # Create a mapping from the reference sequence index to its full annotation
    annotation_map = {i: ref_annotations[best_isotype][i] for i in range(len(ref_annotations[best_isotype]))}

    output_data = []
    input_seq_idx = 0
    ref_seq_idx = 0

    for i in range(max_len):
        input_char = aligned_input_str[i]
        ref_char = aligned_ref_str[i]
        note = ""

        if input_char != '-' and ref_char != '-':  # Match or Mismatch
            if input_char != ref_char:
                note = f"mutation ({ref_char} -> {input_char})"

            annot_tuple = annotation_map.get(ref_seq_idx, ['-'] * 7)
            output_data.append({
                "index": i + 1, "AA": input_char,
                "eu": annot_tuple[1], "kabat": annot_tuple[2], "imgt-unique": annot_tuple[3],
                "imgt": annot_tuple[4], "domain": annot_tuple[5], "structure": annot_tuple[6], "note": note
            })
            input_seq_idx += 1
            ref_seq_idx += 1
        elif input_char != '-' and ref_char == '-':  # Insertion
            output_data.append({
                "index": i + 1, "aa": input_char,
                "eu": "-", "kabat": "-", "imgt-unique": "-", "imgt": "-",
                "domain": "insertion", "structure": "-", "note": "insertion"
            })
            input_seq_idx += 1
        elif input_char == '-' and ref_char != '-':  # Deletion
            annot_tuple = annotation_map.get(ref_seq_idx, ['-'] * 7)
            output_data.append({
                "index": i + 1, "aa": "-", "eu": annot_tuple[1], "kabat": annot_tuple[2],
                "imgt-unique": annot_tuple[3], "imgt": annot_tuple[4], "domain": annot_tuple[5],
                "structure": annot_tuple[6], "note": f"deletion ({ref_char})"
            })
            ref_seq_idx += 1

    return output_data, best_isotype

def annotate_isotype_and_constant_regions(hc_sequence):
    """
    Annotates the constant regions of a heavy chain sequence.
    """
    # 1. Load reference data from the file
    ref_sequences, ref_annotations = load_and_parse_reference_data()
    
    if ref_sequences and ref_annotations:
        return analyze_heavy_chain(hc_sequence, ref_sequences, ref_annotations)
    else:
        raise ValueError("Reference data could not be loaded or parsed correctly.")