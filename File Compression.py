import heapq
import os

class BinaryTreeNode:
    
    def __init__(self,value,freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self,other):                    #overloading LessThan function for comparing two nodes
        return self.freq < other.freq

    def __eq__(self,other):                    #overloading EqualsTo function for comparing two nodes
        return self.freq == other.freq
        
class huffman:
    def __init__(self,path):
        self.path = path
        self.__heap = []
        self.__codes = {}
        self.__reverse_codes = {}

    def __make_freq_dict(self,text):
        freq_dict = {}
        for char in text:
            if freq_dict.get(char,0) == 0:
                freq_dict[char] = 0
            freq_dict[char] += 1
        return freq_dict

    def __build_heap(self,freq_dict):
        for key in freq_dict:
            frequency = freq_dict[key]
            binary_tree_node = BinaryTreeNode(key,frequency)
            heapq.heappush(self.__heap,binary_tree_node)

    def __build_binary_tree(self):
            
        while len(self.__heap) > 1:
            bt_node_1 = heapq.heappop(self.__heap)
            bt_node_2 = heapq.heappop(self.__heap)
            new_freq = bt_node_1.freq + bt_node_2.freq
            new_node = BinaryTreeNode(None,new_freq)
            new_node.left = bt_node_1
            new_node.right = bt_node_2
            heapq.heappush(self.__heap,new_node)

    def __build_codes_helper(self,root,curr_bit):
        if root is None:
            return
        
        if root.value is not None:
            self.__codes[root.value] = curr_bit
            return
            
        self.__build_codes_helper(root.left,curr_bit+"0")
        self.__build_codes_helper(root.right,curr_bit+"1")

    def __build_codes(self):
        root = heapq.heappop(self.__heap)
        self.__build_codes_helper(root,"")

    def __get_encoded_text(self,text):
        encoded_text = ""
        for char in text:
            encoded_text += self.__codes[char]

        return encoded_text

    def __get_padded_encoded_text(self,enc_text):
        extra_zeros = 8 - (len(enc_text)%8)
        for i in range(extra_zeros):
            enc_text += "0"

        padded_info = "{0:08b}".format(extra_zeros)
        enc_text = padded_info + enc_text

        return enc_text

    def __get_bytes_array(self,padded_enc_text):
        #print(padded_enc_text)
        array=[]
        for i in range(0,len(padded_enc_text),8):
            byte = padded_enc_text[i:i+8]
            array.append(int(byte,2))            #int function convert byte string into int with base 2 
        
        #print(array)
        return array
        
    
    def compress(self):

        #it splits the path into two parts i.e "c://user/desktop/sample" and ".txt"
        file_name,file_extension = os.path.splitext(self.path)

        #it creates the output path by adding .bin extension
        output_path = file_name + ".bin"                                    

        #open the file from the path
        with open(self.path,'r+') as file , open(output_path,'wb') as output:

            #read the text from the file
            text = file.read()
            text = text.strip()                            #remove leading  and trailing whitespaces
            
            #make freq dictionary
            freq_dict = self.__make_freq_dict(text)
            
            if len(freq_dict)==1:
                key = freq_dict[0]
                self.__codes[key]="0"
                
            else:
                #build heap from freq dicionary
                self.__build_heap(freq_dict)
                #creating binary tree from heap
                self.__build_binary_tree()
                #building codes from binary tree
                self.__build_codes()

            #encoding the text from the codes dictionary
            encoded_text = self.__get_encoded_text(text)

            #pad the encoded text
            padded_encoded_text = self.__get_padded_encoded_text(encoded_text)

            #converting into byte array
            array = self.__get_bytes_array(padded_encoded_text)
            bytes_array = bytes(array)                                   #converts array into bytes
            #print(bytes_array)

            #writing into output file
            output.write(bytes_array)
            print("File compressed")
            
        return output_path

    def __remove_padded_info(self,bit_string):
        
        padded_info = bit_string[0:8]
        bit_string = bit_string[8:]
        padded_bits = int(padded_info,2)                        #converts binary string into int with base 2
        bit_string = bit_string[:-padded_bits]
        return bit_string

    def __reverse_codes_dict(self):
        for i in self.__codes:
            self.__reverse_codes[self.__codes[i]] = i

    def __get_decompressed_text(self,bit_string):
        decompressed_text = ""
        position = 0
        
        for i in range(0,len(bit_string)):
            if self.__reverse_codes.get(bit_string[position:i+1],0) != 0:
                decompressed_text += self.__reverse_codes[bit_string[position:i+1]]
                position = i+1
                
        return decompressed_text
        
    def decompress(self,input_path):

        file_name,file_extension = os.path.splitext(input_path)
        output_path = file_name + "_decompressed" + ".txt"
        
        with open(input_path,"rb") as file , open(output_path,"w+") as output:

            bit_string = ""
            byte = file.read(1)
            
            while byte:
                byte = ord(byte)                                    #converts b'\05' into 5 i.e ( binary to int )
                bits = bin(byte)[2:].rjust(8,'0')                   #converts 5 -> '0b101' -> '101' -> '00000101'
                bit_string += bits
                byte = file.read(1)                                 #reading next character from file

            #removing padded bits from the string
            actual_bit_string = self.__remove_padded_info(bit_string)

            #creating reverse dictionary of codes dictionary
            self.__reverse_codes_dict()

            #decompressing the text
            decompressed_text = self.__get_decompressed_text(actual_bit_string)

            #storing the text in the output file
            output.write(decompressed_text)
            print("File decompressed")

        return output_path


path = " "     #path of the file to be compressed
h = huffman(path)
compressed_output_path = h.compress()
decompressed_output_path = h.decompress(compressed_output_path)
