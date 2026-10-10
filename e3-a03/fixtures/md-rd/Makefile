app: main.o
	cc main.o -o app

main.o: main.c unused.h
	cc -c main.c -o main.o

clean:
	rm -f main.o app
