from collections import Counter as ctc
print("yes" if sum(v%2 for v in ctc(input("Matn")).values())<=1 else "No")
