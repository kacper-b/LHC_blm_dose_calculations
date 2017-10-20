# class A:
#     dt = 0
#     def __init__(self, start, end):
#         self.start = start
#         self.end = end
#
#     def __hash__(self):
#         return hash((int(self.start), int(self.end)))
#
#     def __eq__(self, other):
#         return isinstance(other, self.__class__) and abs(self.start - other.start) < A.dt and abs(self.end - other.end) < A.dt
#
#     def __lt__(self, other):
#         return isinstance(other, self.__class__) and self.start < other.start + A.dt and self.end < other.end + A.dt
#
#     def __le__(self, other):
#         return self == other or self < other
#
#     def __ne__(self, other):
#         return not self == other
#
#     def __gt__(self, other):
#         return isinstance(other, self.__class__) and self.start > other.start + A.dt and self.end > other.end + A.dt
#
#     def __ge__(self, other):
#         return self == other or self > other
#     def __str__(self):
#         return str(self.start) + ' ' + str(self.end)
#
# from sortedcollections import SortedSet
#
#
# a = [A(1,1.2),A(1,1.2),A(2.,3.)]
# b = [A(1,1.2),A(2.,1.2),A(2.,3.)]
#
# x = SortedSet(a)
# y = SortedSet(b)
#
#
# print(list(map(str,x)), list(map(str,y)))
#
# print(list(map(str,y-x)))

z = []


try:
    z[1]
except Exception as e:
    print(traceback.format_exc())