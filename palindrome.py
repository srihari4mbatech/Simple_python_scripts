class Palindrome:

    @staticmethod
    def is_palindrome(word):
        strk=word
        if len(word)%2>0:
            k=int((len(word)-1)/2)
        else:
            k=int(len(word)/2)
        for t in range(int(k)+1):
            if word[t-1].upper()!= word[-t].upper():
                #print(word[t-1],word[-t],t)
                return False
        return True

print(Palindrome.is_palindrome('Deleveled'))