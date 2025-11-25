CC = gcc
CFLAGS = -Wall -Wextra -O2
SRC = src/lsa.c
TARGET = lsa
PREFIX = /usr/local

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

install: $(TARGET)
	install -d $(PREFIX)/bin
	install -m 755 $(TARGET) $(PREFIX)/bin/

clean:
	rm -f $(TARGET)

uninstall:
	rm -f $(PREFIX)/bin/$(TARGET)
