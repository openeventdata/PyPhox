# PyPhox
Python tools for working with the Phoenix event dataset
([phoenixdata.org](http://phoenixdata.org)).

##Requirements

`PyPhox` currently requires `requests` and `lxml`. This will hopefully change
in the near future. Running `pip install -r requirements.txt` should work.

##Usage

To see the full commandline options:

```
python pyphox.py -h
```

To download all of the daily update files:

```
python pyphox.py -t daily -d /path/to/directory
```

`PyPhox` will automatically unzip all of the downloaded files unless explicitly
told not to through the `-U` flag. An additional feature is the ability to
download files in parallel as indicated by the `-P` flag:

```
python pyphox.py -t daily -d /path/to/directory -P
```

`PyPhox` will only download files that don't currently exist in the indicated
directory. In other words, the program won't re-download files. 

Finally, you can also specify a data version using the `-v` flag. The only
version supported at the moment is `current`. This is also the default argument
so this option can be safely ignored for now.

##More Info

This program was authored by John Beieler (jbeieler@caerusassociates). 
