/*
Original code by : https://github.com/Snootlab/lora_chisterapi
Edited by : Ramin Sangesari
*/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <math.h>
#include <RH_RF95.h>
#include <Python.h>

RH_RF95 rf95;

int run = 1;
int hex_mode = 1;

/* Signal the end of the software */
void sigint_handler(int signal)
{
    run = 0;
}

void setup()
{ 
    wiringPiSetupGpio();

    if (!rf95.init()) 
    {
        fprintf(stderr, "Init failed\n");
        exit(1);
    }

    /* Tx Power is from +5 to +23 dbm */
    rf95.setTxPower(23);
    /* There are different configurations
     * you can find in lib/radiohead/RH_RF95.h 
     * at line 437 
     */
    rf95.setModemConfig(RH_RF95::Bw125Cr45Sf128);
    rf95.setFrequency(902.3); /* MHz */
}

void run_py_script()
{
	Py_Initialize();
	PyRun_SimpleString("execfile(\"/home/pi/Desktop/RTFL_Gateway/create_payload.py\")");
	Py_Finalize();
}

void loop()
{

    /* If we receive one message we show on the prompt
     * the address of the sender and the Rx power.
     */
    if( rf95.available() ) 
    {
        uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
        uint8_t len = sizeof(buf);
		//double buf[RH_RF95_MAX_MESSAGE_LEN];
        //double len = sizeof(buf);

        if (rf95.recv(buf, &len)) 
        {
			double  measurement = buf[1]*256 + buf[2] + (double)buf[3]/100;
			measurement = roundf(100*measurement)/100;
			printf("Received: ");
			printf("From Node %d ",buf[0]);
			printf("======> %.2f", measurement);
				printf("\r\n");
			fflush(stdout);
			
			FILE *f = fopen("/home/pi/Desktop/RTFL_Gateway/payload.txt", "w");
			if (f == NULL)
			{
				printf("Error opening file!\n");
				exit(1);
			}

			/* print some text */
			fprintf(f, "%d %f\n", buf[0], measurement);
			fclose(f);
			run_py_script();
        }
     }
}

int main(int argc, char* argv[])
{
    hex_mode=1;
    signal(SIGINT, sigint_handler);

    setup();

    while( run )
    {
        loop();
        usleep(1);
    }

    return EXIT_SUCCESS;
}
