'''
Created on Sep 29, 2012

@author: killua
@e-mail: killua_hzl@163.com
@project home: https://code.google.com/p/python-ictclas/
'''

import os
from ctypes import cdll, c_int, c_char_p, c_buffer

class CodeType:
    CODE_TYPE_UNKNOWN = c_int(0)
    CODE_TYPE_ASCII = c_int(1)
    CODE_TYPE_GB = c_int(2)
    CODE_TYPE_UTF8 = c_int(3)
    CODE_TYPE_BIG5 = c_int(4)

class POSMap:
    ICT_POS_MAP_FIRST = c_int(0)  
    ICT_POS_MAP_SECOND = c_int(1) 
    PKU_POS_MAP_SECOND = c_int(2) 
    PKU_POS_MAP_FIRST = c_int(3)
    
class PyICTCLAS:
    def __init__(self, lib_path = '../lib/ICTCLAS/libICTCLAS50.so'):
        #Load library
        self._lib_path = os.path.abspath(lib_path)
        self._ictclas_lib = cdll.LoadLibrary(self._lib_path)

    def ictclas_init(self, init_dir= '../lib/ICTCLAS'):
        '''
        ICTCLAS initialize
        @param init_dir: path of initialization 
        @return Return true if initialization succeed. Otherwise return false.
        '''
        if self._ictclas_lib == None:
            self._ictclas_lib = cdll.LoadLibrary(self._lib_path)
        
        return self._ictclas_lib._Z12ICTCLAS_InitPKc(c_char_p(init_dir))    

    def ictclas_exit(self):
        '''
        ICTCLAS Exit
        @return Return true if exit succeed. Otherwise return false.
        '''
        if self._ictclas_lib == None:
            self._ictclas_lib = cdll.LoadLibrary(self._lib_path)
            
        return self._ictclas_lib._Z12ICTCLAS_Exitv()
       
    def ictclas_importUserDict(self, filename, code_type):
        '''
        Import user-defined dictionary from a text file.
        @param filename: Text filename for user dictionary
        @param code_type: encoding type 
        @return: The number of lexical entry imported successfully
        '''
        if self._ictclas_lib == None:
            self._ictclas_lib = cdll.LoadLibrary(self._lib_path)
        
        return self._ictclas_lib._Z26ICTCLAS_ImportUserDictFilePKc9eCodeType(c_char_p(filename), code_type)
        
        
        
    def ictclas_paragraphProcess(self, paragraph, code_type, POStagged = True):
        '''
        ICTCLAS Paragraph Process
        @param paragraph: The source paragraph
        @param code_type: The character coding type of the string
        @param POStagged: Judge whether need POS tagging, 0 for no tag; 1 for tagging; default:1.
        @return: Return the result
        '''
        self._ictclas_lib = cdll.LoadLibrary(self._lib_path)
        
        paragraph, length = self.__pargragph_process(paragraph, code_type)
        result = c_buffer(length * 6)
        self._ictclas_lib._Z24ICTCLAS_ParagraphProcessPKciPc9eCodeTypeb(c_char_p(paragraph), 
                                                                          c_int(length),
                                                                          result,
                                                                          code_type,
                                                                          c_int(POStagged))

        return result
    
    def __pargragph_process(self, paragraph, code_type):
        '''
        Get pargragph's length
        @param paragraph: The source paragraph
        @param code_type: The character coding type of the string
        '''
        if not isinstance(paragraph, unicode):
            return paragraph,len(paragraph)
        elif code_type == CodeType.CODE_TYPE_ASCII:
            return paragraph.encode('ascii'), len(paragraph.encode('ascii'))
        elif code_type == CodeType.CODE_TYPE_GB:
            return paragraph.encode('gb2312'), len(paragraph.encode('gb2312'))
        elif code_type == CodeType.CODE_TYPE_UTF8:
            return paragraph.encode('utf8'), len(paragraph.encode('utf8'))
        elif code_type == CodeType.CODE_TYPE_BIG5:
            return paragraph.encode('big5'), len(paragraph.encode('big5'))
        else:
            pass
        
        
    def ictclas_fileProcess(self, source_filename, code_type, target_filename, POStagged = True):
        '''
        Process a text file
        @param source_filename: The source file path to be analysized;
        @param code_type: The character code type of the source file
        @param target_filename: The result file name to store the results.
        @param POStagged: Judge whether need POS tagging, 0 for no tag; 1 for tagging; default:1.
        @return: Return true if processing succeed. Otherwise return false.
        '''
        if self._ictclas_lib == None:
            self._ictclas_lib = cdll.LoadLibrary(self._lib_path)
            
#Delete By Killua 2012/10/06
#There are several unknow problems when function is running. So delete it.
#        return self._ictclas_lib._Z19ICTCLAS_FileProcessPKcS0_9eCodeTypeb(c_char_p(source_filename),
#                                                                          code_type,
#                                                                          c_char_p(target_filename),
#                                                                          c_int(POStagged))
        src_file = file(source_filename, 'r')
        target_file = file(target_filename, 'w')

        result = self.ictclas_paragraphProcess(src_file.read(), code_type, POStagged)
        target_file.write(result.value)
        
    def ictclas_setPOSmap(self, posmap):
        '''
        Select which pos map will use.
        @param posmap: pos map
        @return: Return 1 if excute succeed. Otherwise return 0.
        '''
        if self._ictclas_lib == None:
            self._ictclas_lib = cdll.LoadLibrary(self._lib_path)
            
        return self._ictclas_lib._Z17ICTCLAS_SetPOSmapi(posmap)

    def ictclas_getWordId(self, word, code_type):
        '''
        Get WordId
        @param word: The target word
        @param code_type: The character type 
        @return: The value of the WordID. 
        '''
        word, word_length = self.__pargragph_process(word, code_type)
        
        return self._ictclas_lib._Z17ICTCLAS_GetWordIdPKci9eCodeType(word, word_length)
