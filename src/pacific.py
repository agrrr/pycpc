from src.codes import *


class Pacific:
    
    # The respective generator polynomials for the fields GF(2^k) used in the chip.
    generator_polynomials = {
        4  : [1,0,0,1,1],         # 1+x+x^4
        5  : [1,0,0,1,0,1],
        6  : [1,0,0,0,0,1,1],
        7  : [1,0,0,0,1,0,0,1],
        8  : [1,0,0,0,1,1,1,0,1],
        9  : [1,0,0,0,0,1,0,0,0,1],
        10 : [1,0,0,0,0,0,0,1,0,0,1],
        11 : [1,0,0,0,0,0,0,0,0,1,0,1],
        15 : [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
        16 : [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,1]
    }

    cpc = [None] * 11   # 11 CPC instances are implemented in Pacific.
    
    cpc[0] = CPC([QS(32, 4, gen=generator_polynomials[4])])
    cpc[1] = CPC([TS(12, 4, gen=generator_polynomials[4])])
    cpc[2] = CPC([PC(10, 6, gen=generator_polynomials[10])])
    
    cpc[3] = CPC([QS(42, 7, gen=generator_polynomials[7]),
                  TS(21, 7, gen=generator_polynomials[7])])
    
    cpc[4] = CPC([QS(80, 8, gen=generator_polynomials[8]),
                  PC(10, 8, gen=generator_polynomials[10])])
    
    cpc[5] = CPC([QS(66, 11, gen=generator_polynomials[11]),
                  TS(33, 11, gen=generator_polynomials[11]),
                  PC(16, 11, gen=generator_polynomials[16])])
    
    cpc[6] = CPC([QS(48, 6, gen=generator_polynomials[6]),
                  PC(9, 6, gen=generator_polynomials[9]),
                  PC(7, 6, gen=generator_polynomials[7])])
    
    cpc[7] = CPC([PC(15, 9, gen=generator_polynomials[15]),
                  PC(10, 9, gen=generator_polynomials[10])])
    
    cpc[8] = CPC([TS(15, 5, gen=generator_polynomials[5]),
                  PC(8, 5, gen=generator_polynomials[8])])

    cpc[9] = CPC([QS(120, 10, gen=generator_polynomials[10])])
    cpc[10] = CPC([QS(132, 6, gen=generator_polynomials[6])])


if __name__ == '__main__':
    for cpc in Pacific.cpc:
        test_code(cpc, 1)
