char input;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int values[3];
  
  // Generate random values
  for (int i = 0; i < 3; i++) {
    values[i] = random(0, 100);  // Generate random values between 0 and 99
  }
  
  // Print values in the desired format
    Serial.print("F:");
    Serial.print(values[0]);
    Serial.print(",");
    Serial.print("P:");
    Serial.print(values[1]);
    Serial.print(",");
    Serial.print("O:");
    Serial.print(values[2]);
  

  Serial.print("\n");
  
  delay(100);  // Delay for 100 milliseconds (0.1 seconds)

  if(Serial.available()){
        input = Serial.read();

        if (input == 'F') {
          digitalWrite(LED_BUILTIN, HIGH);
        }
        else if (input == 'O') {
          digitalWrite(LED_BUILTIN, LOW);
        }
        else if (input == 'P') {
          for (int i = 0; i < 5; i++) { // Flash 5 times
          digitalWrite(LED_BUILTIN, HIGH); // Turn LED on
          delay(100); // Wait for 100 milliseconds
          digitalWrite(LED_BUILTIN, LOW); // Turn LED off
          delay(100); // Wait for 100 milliseconds
        }
        }
}}
 
    
    


