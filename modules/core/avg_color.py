class avg_color():
    def __init__(self,channels):
        self.channels = channels
        self.channels_sum = [0] * self.channels

    def len(self):
        return len(self.channels_sum)

    def sum(self):
        return sum(self.channels_sum)


    def __truediv__(self, other):
        self.channels_sum = list(map(lambda x:x//other,self.channels_sum))
        return self.channels_sum

    def __idiv__(self, other):
        return self.__truediv__(other)

    def __iadd__(self, other):
        other = list(map(int,other))
        if len(other)>self.channels:
            raise Exception("a lot of numbers while adding color")
        else:
            for i,color in enumerate(other):
                self.channels_sum[i]+=color

        return self

    def __iter__(self):
        return iter(self.channels_sum)

    def __str__(self):
        return str(self.channels_sum)