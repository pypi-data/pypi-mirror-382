## checksum_dict
checksum_dict's objects handle the simple but repetitive task of checksumming addresses before setting/getting dictionary values.

### Installation
`pip install checksum_dict`

---
### Usage
There are only two things you must know...

##### ChecksumAddressDict
```
from checksum_dict import ChecksumAddressDict

d = ChecksumAddressDict()
lower = "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"
d[lower] = True
print(d)
>>> ChecksumAddressDict({'0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB': True})
print(d[lower])
>>> True
```
As you can see, the lowercase key `lower` was checksummed and both the key and value were added to the dict as you would expect.

##### DefaultChecksumDict
We also have a checksummed version of a defaultdict:
```
from checksum_dict import DefaultChecksumDict

default = int
d = DefaultChecksumDict(default)
print(d[lower])
>>> 0
```
Although the key was not found in the dictionary, the `default`, in this case `int`, was called and returned a 0, just like with a traditional defaultdict!

---
### Summary
Okay, now that's about it. I hope you all get immense value from this simple yet powerful tool. Now get out there and let's do some buidling!
