# MindWrite
The proposed project aims to develop a computer vision-based virtual mouse that allows for hands-free computer interaction
In this software you will see that we can interact with the computer using head movements and various gestures.  In the following program you will see 3 main operations:

- Left_Blink : Allows you to left click on an item
- Right_Blink: Allows you to right click on an item
- Mouth Open: Allows you to use speech for inputing text 

The program uses the mediapipe library in order to detect the face of the user. 
It creates a facemesh of the user and using the following index values and coordinates we detect where certain features of the face are(right eye, left eye, mouth, nose).
The program uses the nose as a reference in order to move the mouse pointer of the system. 
The program also includes a speech to text converter in order to input text. This can be activated if the program detects if the mouth has been open for longer than 2 seconds.




