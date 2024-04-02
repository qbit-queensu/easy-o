char input;  
float O_value;
float angle = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int values[2];
  
  // Generate random values
  for (int i = 0; i < 2; i++) {
    values[i] = random(10, 30);  // Generate random values between 0 and 99
  }
  
  // Print values in the desired format
  Serial.print("F:");
  Serial.print(values[0]);
  Serial.print(",");
  Serial.print("P:");
  Serial.print(values[1]);
  
  O_value = sin(angle);

  Serial.print(",");
  Serial.print("O:");
  Serial.print(O_value);

  angle += 0.01;

  Serial.print("\n");
  
  delay(100);  // Delay for 100 milliseconds (0.1 seconds)

  if(Serial.available()){
        input = Serial.read();

        if (input == 'v') {
          for (int i = 0; i < 5; i++) { // Flash 5 times
          digitalWrite(LED_BUILTIN, HIGH); // Turn LED on
          delay(100); // Wait for 100 milliseconds
          digitalWrite(LED_BUILTIN, LOW); // Turn LED off
          delay(100); // Wait for 100 milliseconds
        }
        }
}}
 
    
    


