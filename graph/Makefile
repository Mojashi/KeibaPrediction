CFLAGS := -O3 -lmysqlclient -lpython3.6m -I/usr/include/python3.8
LIBS := graph.cpp sql.cpp

test: test.cpp $(LIBS)
	g++ test.cpp $(LIBS) $(CFLAGS) -o test
prod: prod.cpp $(LIBS)
	g++ prod.cpp $(LIBS) $(CFLAGS) -o prod
run: test
	./test