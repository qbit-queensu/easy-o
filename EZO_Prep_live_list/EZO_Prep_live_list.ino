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
    Serial.print("f");
    Serial.print(values[0]);
    Serial.print(",");
    Serial.print("p");
    Serial.print(values[1]);
    Serial.print(",");
    Serial.print("o");
    Serial.print(values[2]);
  

  Serial.print("\n");
  
  delay(100);  // Delay for 100 milliseconds (0.1 seconds)
}
