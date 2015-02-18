all: lunar wordexp.so

.PHONY: lunar

lunar: 
	$(MAKE) -C lunar

wordexp.so: wordexp.o
	gcc -pthread -shared -Wl,-O1 wordexp.o -L/usr/lib -lpython2.7 -o wordexp.so

wordexp.o: wordexp.c
	gcc -fno-strict-aliasing -O2 -g \
		-pipe -DNDEBUG -g -fwrapv -Os -Wall -Wstrict-prototypes -fPIC \
		-I/usr/include/python2.7 -c wordexp.c -o wordexp.o
