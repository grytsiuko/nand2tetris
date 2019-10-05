// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.



(MAIN)

	// addr - current screen register
	@SCREEN
	D=A
	@addr
	M=D

	// i - remaining registers
	@8192
	D=A
	@i
	M=D
	
	// color - 0 (white) or -1 (black)
	@color
	M=0
	@KBD
	D=M
	@LOOP
	D;JEQ
	@color
	M=-1

(LOOP)

	// if i == 0 end loop
	@i
	D=M
	@END
	D;JEQ

	// otherwise 
	// change screen register
	@color
	D=M
	@addr
	A=M
	M=D

	// addr++
	@addr
	M=M+1

	// i--
	@i
	M=M-1

	@LOOP
	0;JMP

(END)

	@MAIN
	0;JMP