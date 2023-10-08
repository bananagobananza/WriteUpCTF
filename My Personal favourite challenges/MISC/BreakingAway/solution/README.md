Extract the zip file give us the pdf 

Using ```strings breaking-away.pdf | head``` to obtain the header we got

```
%PDF-1.4
1 0 obj
/Type /Pages
/Count 4
/Kids [ 4 0 R 22 0 R 26 0 R 30 0 R ]
endobj
2 0 obj
/Producer (PyPDF2)
ip_creator (3\056225\05642\05693)
time_creator (2021\05509\05528\04012\07200\07200\040\055400)
```

notice \056 is an octal escape sequence represents ASCII code for "."
so 3\056225\05642\05693 can be translate --> 3.225.42.93