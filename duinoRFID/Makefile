PORT=/dev/ttyUSB0
BOARD=arduino:avr:nano:cpu=atmega328old
BOARD_oLD=bare-conductive-arduino:avr:baretouch
compile:
				arduino-cli compile --fqbn $(BOARD)
upload:
				arduino-cli upload -p $(PORT) --fqbn $(BOARD)
makeme: compile upload
all: makeme
serial:
		minicom -b 115200 -o -D $(PORT)
clean:
			m -r build

dep:
	arduino-cli core install arduino:avr

lib:
	arduino-cli lib install "MFRC522" "MPR121"
