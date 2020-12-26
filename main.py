from TXTRConverter import TXTRConverter

if __name__ == '__main__':
    
    filename = 'TXTR_ElevatorIcon_1.TXTR'

    con = TXTRConverter(filename)
    con.save_as_png()