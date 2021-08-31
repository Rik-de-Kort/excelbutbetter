'''
First order of business is to write a parser. See Jupyter.

A)It shall implement at least the limits defined in the “Basic Limits” section. 3.7  -> Not a problem though does need tests

B)It shall implement the syntax defined in these sections on syntax: -> Best follow Excel spec here (page 2050)
    Criteria 4.11.11; I don't think this one is useful yet
    Basic Expressions 5.2; forced recalc not part of Excel
    Constant Numbers 5.3;
    Constant Strings 5.4;
    Operators 5.5;
    Functions and Function Parameters 5.6;
    Nonstandard Function Names 5.7; -> Not going to do this
    References 5.8; -> Cell reference intra-file only, need some story for interop but that can come later
    Reference operators -> : for range, comma for union, space for intersection 
    Simple Named Expressions ;
    Errors 5.12; -> #DIV/0, #N/A, #NAME?, #NULL!, #NUM!, #REF!, #VALUE! Note: write this in an option type
    Whitespace 5.14. 

C)It shall implement all implicit conversions for the types it implements, at least Text 6.3.14, Conversion to Number 6.3.5, Reference , Conversion to Logical 6.3.12, and when an expression returns an Error. 

D)It shall implement the following operators (which are all the operators except reference union (~)):
    Infix Operator Ordered Comparison ("<", "<=", ">", ">=") 6.3.5; Delegate to Python, mind Excel number conversion semantics
    Infix Operator "&” 6.4.10; Text concatenation, ie. lambda s, t: str(s) + str(t)
    Infix Operator "+” 6.4.2; Unsure if want to typecheck for str here.
    Infix Operator "-” 6.4.3;
    Infix Operator "*” 6.4.4;
    Infix Operator "/” 6.4.5;
    Infix Operator "^” 6.4.6;  Exponentiation!
    Infix Operator "=” 6.4.7; Equality (== in Python)
    Infix Operator "<>” 6.4.8; Inequality (!= in Python)
    Postfix Operator “%” 6.4.14; Divide value by 100, format as percentage, ie 10% == 0.10
    Prefix Operator “+” 6.4.15; Not in Excel, skip
    Prefix Operator “-” 6.4.16; Unary minus
    Infix Operator Reference Intersection ("!") 6.4.12; This is already present as space
    Infix Operator Range (":") 6.4.11. 

E)It shall implement at least the following functions as defined in this specification:
    ABS 6.16.2 ;
    ACOS 6.16.3 ;
    AND 6.15.2 ;
    ASIN 6.16.7 ;
    ATAN 6.16.9 ;
    ATAN2 6.16.10 ;
    AVERAGE 6.18.3 ;
    AVERAGEIF 6.18.5 ;
    CHOOSE 6.14.3 ;
    COLUMNS 6.13.5 ;
    COS 6.16.19 ;
    COUNT 6.13.6 ;
    COUNTA 6.13.7 ;
    COUNTBLANK 6.13.8 ;
    COUNTIF 6.13.9 ;
    DATE 6.10.2 ;
    DAVERAGE 6.9.2 ;
    DAY 6.10.5 ;
    DCOUNT 6.9.3 ;
    DCOUNTA 6.9.4 ;
    DDB 6.12.14 ;
    DEGREES 6.16.25 ;
    DGET 6.9.5 ;
    DMAX 6.9.6 ;
    DMIN 6.9.7 ;
    DPRODUCT 6.9.8 ;
    DSTDEV 6.9.9 ;
    DSTDEVP 6.9.10 ;
    DSUM 6.9.11 ;
    DVAR 6.9.12 ;
    DVARP 6.9.13 ;
    EVEN 6.16.30 ;
    EXACT 6.20.8 ;
    EXP 6.16.31 ;
    FACT 6.16.32 ;
    FALSE 6.15.3 ;
    FIND 6.20.9 ;
    FV 6.12.20 ;
    HLOOKUP 6.14.5 ;
    HOUR 6.10.10 ;
    IF 6.15.4 ;
    INDEX 6.14.6 ;
    INT 6.17.2 ;
    IRR 6.12.24 ;
    ISBLANK 6.13.14 ;
    ISERR 6.13.15 ;
    ISERROR 6.13.16 ;
    ISLOGICAL 6.13.19 ;
    ISNA 6.13.20 ;
    ISNONTEXT 6.13.21 ;
    ISNUMBER 6.13.22 ;
    ISTEXT 6.13.25 ;
    LEFT 6.20.12 ;
    LEN 6.20.13 ;
    LN 6.16.39 ;
    LOG 6.16.40 ;
    LOG10 6.16.41 ;
    LOWER 6.20.14 ;
    MATCH 6.14.9 ;
    MAX 6.18.45 ;
    MID 6.20.15 ;
    MIN 6.18.48 ;
    MINUTE 6.10.12 ;
    MOD 6.16.42 ;
    MONTH 6.10.13 ;
    N 6.13.26 ;
    NA 6.13.27 ;
    NOT 6.15.7 ;
    NOW 6.10.15 ;
    NPER 6.12.29 ;
    NPV 6.12.30 ;
    ODD 6.16.44 ;
    OR 6.15.8 ;
    PI 6.16.45 ;
    PMT 6.12.36 ;
    POWER 6.16.46 ;
    PRODUCT 6.16.47 ;
    PROPER 6.20.16 ;
    PV 6.12.41 ;
    RADIANS 6.16.49 ;
    RATE 6.12.42 ;
    REPLACE 6.20.17 ;
    REPT 6.20.18 ;
    RIGHT 6.20.19 ;
    ROUND 6.17.5 ;
    ROWS 6.13.30 ;
    SECOND 6.10.16 ;
    SIN 6.16.55 ;
    SLN 6.12.45 ;
    SQRT 6.16.58 ;
    STDEV 6.18.72 ;
    STDEVP 6.18.74 ;
    SUBSTITUTE 6.20.21 ;
    SUM 6.16.61 ;
    SUMIF 6.16.62 ;
    SYD 6.12.46 ;
    T 6.20.22 ;
    TAN 6.16.69 ;
    TIME 6.10.17 ;
    TODAY 6.10.19 ;
    TRIM 6.20.24 ;
    TRUE 6.15.9 ;
    TRUNC 6.17.8 ;
    UPPER 6.20.27 ;
    VALUE 6.13.34 ;
    VAR 6.18.82 ;
    VARP 6.18.84 ;
    VLOOKUP 6.14.12 ;
    WEEKDAY 6.10.20 ;
    YEAR 6.10.23 
'''

