// Versión con grabación de datos en Excel para pruebas simulación 4G para ENEDIS

// Bibliotecas
  #include <LCDWIKI_GUI.h>                          // Core graphics library
  #include <LCDWIKI_KBV.h>                          // Hardware-specific library
  LCDWIKI_KBV my_lcd(ILI9486,A3,A2,A1,A0,A4);       // model,cs,cd,wr,rd,reset
  unsigned long show_text(void);

//Parameters
  const int clk_S1_Pin  = 34;                       // Contacto del Rotary
  const int dt_S2_Pin  = 35;                        // Contacto del Rotary
  const int Pulsador_Rotary = 36;                   // Pulsador del Rotary
  const int Pulsador = 38;                          // Pulsador de cambio de estado
  const int LED_Pulsador = 31;                      // LED rojo del pulsador de cambio de estado
  const int CMD_RELAY = 18;                         // LLeva la INT_5
  const int CMD_OUT = 19;                           // Lleva la INT_4
  const int CMD_IN = 20;                            // Lleva la INT_3
  int Periodos[5]={100, 200, 250, 500, 1000};
  unsigned long N_Ordenes[9]={1, 10, 25, 50, 100, 500, 1000, 10000, 100000};
  int Tac[4]={10, 15, 25, 250};

  //Variables Rotary
  int Valor_Rot1 = 0;                               //P osición para Períodos       100ms
  int Valor_Rot2 = 1;                               // Posición para N_Ordenes      10
  int Valor_Rot3 = 0;                               // Posición para Tac            10ms
  bool clk_S1_State  = LOW;
  bool clk_S1_Last  = HIGH;
  bool Estado_Pulsador_Rotary = HIGH;
  bool Ultimo_Estado_Pulsador_Rotary = HIGH;
  unsigned int BotonRotary  = 1;

  //Variables Pulsador
  bool Pulsador_State = HIGH;
  bool Pulsador_Last = HIGH;

// Variables TKTK
  bool CMD_RELAY_State = LOW;
  bool TKTK_State = LOW;                            // LOW: adquisición de datos     HIGH: Generación de órdenes y medida de tiempos
  unsigned long Tiempo_Anterior = 0;
  unsigned long T_OUT = 0;
  unsigned long T_IN = 0;
  volatile unsigned long T_OUT_INT = 0;
  volatile unsigned long T_IN_INT = 0;
  float T_Disparo = 0;
  float T_Disparo_Min = 100000;
  float T_Disparo_Max = 0;
  float T_Disparo_Medio = 0;
  float T_Disparo_Total = 0;
  float Pmc = 0;
  float Contador_Recibidos = 0;
  float Contador_Emitidos = 0;
  float Contador_Validos = 0;
  unsigned long Tiempo = 0;
  unsigned long Horas = 0;
  unsigned long Minutos = 0;
  unsigned long Segundos = 0;
  int i = 0;
  int Color = 0;
  int Distribution[251];
  float L=0;

  // Variables para el parser de comandos
  String serialBuffer = "";
  bool commandReady = false;



// Inicialización
  void setup() {
  // Inicialización pantalla
    Serial.begin(9600);
    my_lcd.Init_LCD();
    my_lcd.Fill_Screen(37,212,245);  
    my_lcd.Set_Rotation(3); 
    my_lcd.Set_Text_colour(0, 0,255); 
    my_lcd.Set_Text_Back_colour(37,212,245);    
    my_lcd.Set_Text_Size(2);
    my_lcd.Set_Text_Mode(0);
  // Init Rotary
    pinMode(clk_S1_Pin,INPUT);
    pinMode(dt_S2_Pin,INPUT);
    pinMode(Pulsador_Rotary,INPUT_PULLUP);
  // Inicialización Pulsador
    pinMode(Pulsador, INPUT);
    pinMode(LED_Pulsador, OUTPUT);
  // Inicialización TKTK
    pinMode (CMD_RELAY, OUTPUT);
    pinMode (CMD_OUT, INPUT_PULLUP);
    pinMode (CMD_IN, INPUT_PULLUP);

    // attachInterrupt(digitalPinToInterrupt(CMD_OUT),Deteccion_CMD_OUT,FALLING);    // Interrupción para detección de orden de salida
    // attachInterrupt(digitalPinToInterrupt(CMD_IN),Deteccion_CMD_IN,FALLING);      // Interrupción para detección de orden de entrada
  // Inicialización textos pantalla
    my_lcd.Print_String("V6-Remoto", 350, 15);
    my_lcd.Print_String("Esperando CMD...", 50, 15);

    // my_lcd.Print_String("V6",430,15);
    // my_lcd.Print_String("T:",50,15);
    // my_lcd.Print_String("Cmd length:       ms",50,50);
    // my_lcd.Print_String(">",30, 50);
    // //my_lcd.Print_String("<",300, 50);
    // my_lcd.Print_String("N of Cmd:",50,75);
    // my_lcd.Print_String("Tac max:          ms",50,100);
    // my_lcd.Print_String("Cmd Tx:",50,140);
    // my_lcd.Print_String("Cmd Rx:",50,165);
    // Vaciar_Pantalla();
    // my_lcd.Print_Number_Int(Periodos[Valor_Rot1],185,50,0,0,10);
    // my_lcd.Print_Number_Int(N_Ordenes[Valor_Rot2],185,75,0,0,10);
    // my_lcd.Print_Number_Int(Tac[Valor_Rot3],185,100,0,0,10);
    // Calculo_Duracion();
  }

// void loop() 
//   {
//   if (TKTK_State == LOW) {
//     my_lcd.Print_String("       ",185,15);
//     my_lcd.Print_String("STOPPED",185,15);
//     Configuracion_TKTK();
//     Pulsador_State = digitalRead(Pulsador);
//         if (Pulsador_State == LOW) {
//         delay(500);
//         TKTK_State = HIGH;}
  
//   } else {
//       Vaciar_Pantalla();
//       Inicializar_Resultados();
//       my_lcd.Print_String("       ",185,15);
//       my_lcd.Print_String("RUNNING",185,15); 
//       Generacion_Ordenes();
    
//       Calculo_Resultados();
//       Presentacion_Resultados();
//       Grabacion_resultados();
//     } 
//   }                                                           // Cierre del loop()

void loop() {
  readSerial();   // Función que lee el puerto serie

  if (commandReady) {   // Una vez la función readSerial ha leído todo el comando, ésta pondrá commandReady a '1'
    parseCommand(serialBuffer);   // Una vez tenemos todo el comando -> Lo parseamos
    
    // Limpiamos el bufer para captar el siguiente comando
    serialBuffer = "";
    commandReady = false;
  }
}

void readSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {  // Cuando lee un \n, el comando ha terminado. Ponemos command ready a True
      commandReady = true;
    } else {
      serialBuffer += c;  // Si no llega el \n -> Seguimos leyendo
    }
  }
}

void parseCommand(String cmd) {
  cmd.trim(); // Limpia espacios en blanco

  if (cmd == "PING") {
    Serial.println("PONG_ARDUINO");
    return;
  }



  // Nuestro comando de ráfaga será: "B:<num>:<dur>:<del>"
  // Ejemplo: "B:10:500:1000" (10 pulsos, 500ms ON, 1000ms OFF)
  if (cmd.startsWith("B:")) {
    // Extraemos los parámetros
    long num_pulses = 0;
    long duration_ms = 0;
    long delay_ms = 0;
    // Si partieramos de B:10:500:1000
    // Guardamos a partir de los dos primeros caracteres ('B:')
    String params = cmd.substring(2);   // params = 10:500:1000
    
    // Buscamos el primer separador ":"
    int first_last_cmd_indx = params.indexOf(':');   // Necesitamos encontrar el indice del proximo ':' para despues acotar con substring
    num_pulses = params.substring(0, first_last_cmd_indx).toInt();
    
    // Buscamos el segundo separador ":"
    int second_last_cmd_indx = params.indexOf(':', first_last_cmd_indx + 1);   // Esta vez le indicamos a indexOf cuando tiene que empezar la busqueda (despues del indice del : que habíamos encontrado antes)
    duration_ms = params.substring(first_last_cmd_indx + 1, second_last_cmd_indx).toInt();
    
    // El resto es el delay (delay entre rafagas! no entre pulsos (esto está dentro de la fnci))
    delay_ms = params.substring(second_last_cmd_indx + 1).toInt();

    // Ejecuta la ráfaga con los parámetros recibidos
    executeRemoteBurst(num_pulses, duration_ms, delay_ms);
    Serial.println("ACK,BURST_COMPLETED");
    return;
  }

  // Comando de pulso simple: "P:<dur>" (ej: "P:500")
  if (cmd.startsWith("P:")) {
    long duration_ms = cmd.substring(2).toInt();
    digitalWrite(CMD_RELAY, HIGH);
    digitalWrite(LED_Pulsador, HIGH);
    delay(duration_ms);
    digitalWrite(CMD_RELAY, LOW);
    digitalWrite(LED_Pulsador, LOW);
    Serial.println("ACK,PULSE_COMPLETED");
    return;
  }

  Serial.println("ERROR,CMD_UNKNOWN");
}


void executeRemoteBurst(long num_pulses, long duration_ms, long delay_ms) {
  
  // No usamos el feedback T_IN para la activación de entradas de momento...
  
  for (long i = 0; i < num_pulses; i++) {
    // Pulso ON
    digitalWrite(CMD_RELAY, HIGH);
    digitalWrite(LED_Pulsador, HIGH);
    
    // Esperamos a que finalice el pulso ON
    delay(duration_ms);

    // Pulso OFF
    digitalWrite(CMD_RELAY, LOW);
    digitalWrite(LED_Pulsador, LOW);

    // Esperamos a que finalice el pulso OFF (solo si no es el último pulso, ya que en este caso, los digitalWrite de antes ya han actuado a LOW. Pero como queremos que se queden "permanentemente" así, no hace falta hacer la espera)
    if (i < num_pulses - 1) {
      delay(delay_ms);
    }
  }
}



// //Lectura de la configuración: Período, nº de disparos y Tac
//   void Configuracion_TKTK(){
//   do{
//       Lectura_Pulsador_Rotary();
//       if (BotonRotary == 1)
//           {readRotary1();                                      // Si BotonRotary == 1 leemos Duración de Órdenes
//               } else { if (BotonRotary == 2)
//                       {readRotary2();                          // Si BotonRotary == 2 leemos Número de Órdenes
//                           } else {readRotary3();              // Si BotonRotary == 3 leemos Tac
//                                   }
//                       }
//     }while (TKTK_State == LOW);
//   }

// //Selección de la duración de orden
//   void readRotary1() 
//   {  
//   do{
//     Lectura_Pulsador_Rotary();
//     clk_S1_State = digitalRead(clk_S1_Pin);
//     if ((clk_S1_Last == LOW) && (clk_S1_State == HIGH)) {      //rotary moving
//         if (digitalRead(dt_S2_Pin) == HIGH) {
//         Valor_Rot1 = Valor_Rot1 - 1;
//         if ( Valor_Rot1 < 0 ) {
//           Valor_Rot1 = 0;
//         }
//       } else {
//         Valor_Rot1++;
//         if ( Valor_Rot1 > 4 ) {
//           Valor_Rot1 = 4;
//         }
//       }
//       my_lcd.Print_String("     ",185,50);
//       my_lcd.Print_Number_Int(Periodos[Valor_Rot1],185,50,0,0,10);
//       Calculo_Duracion(); 
//     }
//     clk_S1_Last = clk_S1_State;
//     Lectura_Pulsador();
//   } while(BotonRotary == 1 && TKTK_State == LOW);
//   }

// //Selección del número de órdenes a generar
//   void readRotary2() 
//     {  
//     do{
//     Lectura_Pulsador_Rotary();
//     clk_S1_State = digitalRead(clk_S1_Pin);
//       if ((clk_S1_Last == LOW) && (clk_S1_State == HIGH)) {       //rotary moving
//           if (digitalRead(dt_S2_Pin) == HIGH) {
//           Valor_Rot2 = Valor_Rot2 - 1;
//           if ( Valor_Rot2 < 0 ) {
//             Valor_Rot2 = 0;
//           }
//         } else {
//           Valor_Rot2++;
//           if ( Valor_Rot2 > 8 ) {
//             Valor_Rot2 = 8;
//           }
//         }
//         my_lcd.Print_String("         ",185,75);
//         my_lcd.Print_Number_Int(N_Ordenes[Valor_Rot2],185,75,0,0,10);
//         Calculo_Duracion();
//       }
//       clk_S1_Last = clk_S1_State;
//       Lectura_Pulsador();
//     } while(BotonRotary == 2 && TKTK_State == LOW);
//     }

// //Selección de Tac
//   void readRotary3() 
//   {  
//   do{
//   Lectura_Pulsador_Rotary();
//   clk_S1_State = digitalRead(clk_S1_Pin);
//     if ((clk_S1_Last == LOW) && (clk_S1_State == HIGH)) {      //rotary moving
//         if (digitalRead(dt_S2_Pin) == HIGH) {
//         Valor_Rot3 = Valor_Rot3 - 1;
//         if ( Valor_Rot3 < 0 ) {
//           Valor_Rot3 = 0;
//         }
//       } else {
//         Valor_Rot3++;
//         if ( Valor_Rot3 > 3 ) {
//           Valor_Rot3 = 3;
//         }
//       }
//       my_lcd.Print_String("     ",185,100);
//       my_lcd.Print_Number_Int(Tac[Valor_Rot3],185,100,0,0,10);
//     }
//     clk_S1_Last = clk_S1_State;
//     Lectura_Pulsador();
//   } while(BotonRotary == 3 && TKTK_State == LOW);
//   int Distribution[Tac[Valor_Rot3]+1];
//   }

// void Lectura_Pulsador_Rotary()
//   { Estado_Pulsador_Rotary = digitalRead(Pulsador_Rotary);
//     if (Estado_Pulsador_Rotary == LOW && Ultimo_Estado_Pulsador_Rotary == HIGH) {
//     delay(150);
//     BotonRotary++;
//         if (BotonRotary == 4) {
//         BotonRotary = 1;
//         }
//     Ultimo_Estado_Pulsador_Rotary = HIGH;
//        if (BotonRotary == 1) {
//               // my_lcd.Print_String(" ",300, 75);
//               // my_lcd.Print_String(" ",300, 100);
//               // my_lcd.Print_String("<",300, 50);  
//               my_lcd.Print_String(" ",30, 75);
//               my_lcd.Print_String(" ",30, 100);
//               my_lcd.Print_String(">",30, 50);
//                  } else { if (BotonRotary == 2) {
//                      // my_lcd.Print_String(" ",300, 50);
//                      // my_lcd.Print_String(" ",300, 100);
//                      // my_lcd.Print_String("<",300, 75);
//                      my_lcd.Print_String(" ",30, 50);
//                      my_lcd.Print_String(" ",30, 100);
//                      my_lcd.Print_String(">",30, 75);
//                      } else { if (BotonRotary == 3) {
//                          // my_lcd.Print_String(" ",300, 50);
//                          // my_lcd.Print_String(" ",300, 75);
//                          // my_lcd.Print_String("<",300, 100);
//                          my_lcd.Print_String(" ",30, 50);
//                          my_lcd.Print_String(" ",30, 75);
//                          my_lcd.Print_String(">",30, 100);
//                                                      }
//                             }
//                         }
//       }
//   }  

// void Lectura_Pulsador()
//   {
//     Pulsador_State = digitalRead(Pulsador);
//         if (Pulsador_State == LOW) {
//         delay(500);
//         TKTK_State = HIGH;
//         }
//   }

// //Generación de órdenes de disparos según configuración y lectura de tiempos
//   void Generacion_Ordenes() 
//   {
//     Contador_Emitidos = 0;
//     Contador_Recibidos = 0;
//     Contador_Validos = 0;
//     CMD_RELAY_State = HIGH;
//     Tiempo_Anterior = millis();
//     digitalWrite(CMD_RELAY, CMD_RELAY_State);
//     digitalWrite(LED_Pulsador, CMD_RELAY_State);
//   do {
//     if (millis()-Tiempo_Anterior >= Periodos[Valor_Rot1]) {
//     CMD_RELAY_State = !CMD_RELAY_State;
//     digitalWrite(CMD_RELAY, CMD_RELAY_State);
//     digitalWrite(LED_Pulsador, CMD_RELAY_State);
//     Tiempo_Anterior = millis();
//     }
//     if (CMD_RELAY_State == HIGH) {
//         if (T_OUT_INT > 0) {
//             T_OUT = T_OUT_INT;
//             T_OUT_INT = 0;
//             Contador_Emitidos++;
//             }
//             if (T_IN_INT > 0 && (T_IN_INT - T_IN >200)) {
//             T_IN = T_IN_INT;
//             T_IN_INT = 0;
//             Contador_Recibidos++;
//             T_Disparo = (T_IN - T_OUT);   
//           T_Disparo_Total = T_Disparo + T_Disparo_Total;
//           if (T_Disparo / 1000 <= Tac[Valor_Rot3]) {
//             Contador_Validos++;
//             Distribution[int(T_Disparo / 1000)]++;
//           } else {
//             Distribution[Tac[Valor_Rot3]+1]++;
//           }
//         if (T_Disparo > T_Disparo_Max) {
//               T_Disparo_Max = T_Disparo;
//             }
//         if (T_Disparo < T_Disparo_Min) {
//             T_Disparo_Min = T_Disparo;
//             }
//       //  Serial.print(Distribution[int(T_Disparo / 1000)]);
//         }
//     }
//           Pulsador_State = digitalRead(Pulsador);
//         if ((CMD_RELAY_State == LOW) && (Pulsador_State == LOW || Contador_Emitidos >= N_Ordenes[Valor_Rot2])) {  
//         delay(500);
//         TKTK_State = LOW;
//       }
//   } while (TKTK_State == HIGH);
//   }

// //Interrupción para determinar el instante de salida de orden
//   void Deteccion_CMD_OUT() 
//   {T_OUT_INT = micros();
//   }

// //Interrupción para determinar el instante de recepción de orden y calcular el tiempo de transmisión
//   void Deteccion_CMD_IN() 
//   {T_IN_INT = micros();
//   }


// void Calculo_Resultados()                                         // Dividido los tiempos por 1000 porque los tiempos están en us
//   { 
//     Pmc = 1000 * (1-Contador_Validos / Contador_Emitidos);
//     T_Disparo_Medio = T_Disparo_Total/1000/Contador_Recibidos;
//     T_Disparo_Min = T_Disparo_Min / 1000;
//     T_Disparo_Max = T_Disparo_Max / 1000;
//   }

// void Presentacion_Resultados()
//   {
//   int maximo = 0;
//   for (int w = 0; w < Tac[Valor_Rot3]+1; w++) {
//         maximo = max(Distribution[w],maximo);
//       }
//           my_lcd.Print_Number_Int(Contador_Emitidos,185,140,0,0,10);
//           my_lcd.Print_Number_Int(Contador_Validos,185,165,0,0,10);
//           my_lcd.Print_Number_Float(Pmc,2,160,205,',',3,' ');
//           my_lcd.Print_Number_Float(T_Disparo_Medio,1,200,230,',',3,' ');
//           my_lcd.Print_Number_Float(T_Disparo_Min,1,200,255,',',3,' ');
//           my_lcd.Print_Number_Float(T_Disparo_Max,1,200,280,',',3,' ');
//           my_lcd.Print_String("Statistics",330,50);
//           my_lcd.Set_Text_Size(1);
//           for(i =0; i<15; i++) {
//             my_lcd.Print_Number_Int(i+1,325,75+14*i,0,0,10);
//               L=100*Distribution[i]/maximo;
//               if (L<1) {
//                 L=0;
//               } else {L=int(L);
//             }
//             my_lcd.Fill_Rect(350,75+14*i,L,5,16);
//         //  Serial.print(L);
//           }
//           my_lcd.Print_String(">Tac",325,75+14*15);
//           my_lcd.Fill_Rect(350,75+14*15,int(150*Distribution[40]/maximo),5,16);
//           my_lcd.Set_Text_Size(2);
//   }

// void Grabacion_resultados() {
//   int Prueba = random(0, 10000); // Número entre 0 y 9999
//   my_lcd.Print_String("       ",185,15);
//   my_lcd.Print_String("     ",315,15);
//   my_lcd.Print_String("SAVING",185,15); 
//   my_lcd.Print_Number_Int(Prueba,315,15,2,' ',10);
//   //Serial.println("CLEARDATA");                  // Limpia la hoja
//   //Serial.println("LABEL,Interval,Rx Com");
//  Serial.print("PRUEBA:"); Serial.print(","); Serial.print(Prueba); Serial.println(",");   // Separador 
//   delay (50); 
//   for (int i = 0; i < 250; i++) {
//     Serial.print(i+1);
//     Serial.print(",");   
//     delay (50);                
//     Serial.print(Distribution[i]);
//     Serial.println(",");             
//     delay(100);
//   } 
//   my_lcd.Print_String("       ",185,15);
//   my_lcd.Print_String("STOPPED",185,15); 
//  }


// void Inicializar_Resultados() {     
//       T_OUT = 0;
//       T_IN = 0;
//       T_OUT_INT = 0;
//       T_IN_INT = 0; 
//       T_Disparo = 0;
//       T_Disparo_Min = 100000;
//       T_Disparo_Max = 0;
//       T_Disparo_Medio = 0;
//       T_Disparo_Total = 0;
//       Pmc = 0;
//       for (int w = 0; w < 251; w++) {
//         Distribution[w]=0;
//       }
//   }    

// void Vaciar_Pantalla()  {
//           my_lcd.Print_String("     ",315,15);                 // Nº de prueba
//           my_lcd.Print_String ("       ",185,140);             // Contador_Emitidos
//           my_lcd.Print_String("       ",185,165);              // Contador_Validos
//           my_lcd.Print_String("Pmc:             E-3",50,205); 
//           my_lcd.Print_String("Tac avg:          ms",50,230);
//           my_lcd.Print_String("Tac min:          ms",50,255);
//           my_lcd.Print_String("Tac max:          ms",50,280);
//           Color=my_lcd.Color_To_565(37,212,245);
//           my_lcd.Fill_Rect(300,50,190,290,Color);
//   }

// void Calculo_Duracion()
//   {
//     Tiempo = 2 * Periodos[Valor_Rot1] * N_Ordenes[Valor_Rot2] / 1000;
//     Horas = int(Tiempo/3600);
//     Minutos = int((Tiempo-Horas*3600)/60);
//     Segundos = Tiempo - Horas*3600 - Minutos * 60;
//     my_lcd.Print_String("  :  :  ",80,15);
//     my_lcd.Print_Number_Int(Horas,80,15,2,' ',10);
//     my_lcd.Print_Number_Int(Minutos,115,15,2,' ',10);
//     my_lcd.Print_Number_Int(Segundos,150,15,2,' ',10);
//   }
  