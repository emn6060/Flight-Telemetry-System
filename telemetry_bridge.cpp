#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <strsafe.h>
#include <ws2tcpip.h>
#include <iostream>
#include "SimConnect.h"

using namespace std;

#pragma comment(lib, "Ws2_32.lib")

// Global Degiskenler
HANDLE hSimConnect = NULL;
int quit = 0;
SOCKET udpSock;
sockaddr_in targetAddr;

// Veri Paketi (Python ile eslesmeli)
struct FlightTelemetry {
    double v_speed;
    double radio_alt;
    double g_force;
    double on_ground; // 1.0 = yerde, 0.0 = havada
};

enum DATA_ID { DEF_TELEM };
enum REQ_ID { REQ_TELEM };

// UDP Baglantisini Hazirla
void setup_udp() {
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    udpSock = socket(AF_INET, SOCK_DGRAM, 0);
    targetAddr.sin_family = AF_INET;
    targetAddr.sin_port = htons(5005);
    inet_pton(AF_INET, "127.0.0.1", &targetAddr.sin_addr);
}

// SimConnect Callback Fonksiyonu
void CALLBACK DispatchHandler(SIMCONNECT_RECV* pData, DWORD cbData, void* pContext)
{
    switch (pData->dwID)
    {
    case SIMCONNECT_RECV_ID_SIMOBJECT_DATA:
    {
        SIMCONNECT_RECV_SIMOBJECT_DATA* pObjData = (SIMCONNECT_RECV_SIMOBJECT_DATA*)pData;
        FlightTelemetry* data = (FlightTelemetry*)&pObjData->dwData;

        // Konsol Log 
        cout << "VS: " << (int)data->v_speed
            << " | RA: " << (int)data->radio_alt
            << " | G: " << data->g_force
            << " | GND: " << data->on_ground << "\n";

        // Python'a gonder
        sendto(udpSock, (const char*)data, sizeof(FlightTelemetry), 0, (sockaddr*)&targetAddr, sizeof(targetAddr));
        break;
    }

    case SIMCONNECT_RECV_ID_QUIT:
    {
        quit = 1;
        break;
    }
    }
}

int __cdecl main(int argc, char* argv[])
{
    setup_udp();
    
    cout << "Flight Telemetry System baslatiliyor...\n";
    cout << "Simulator baglantisi bekleniyor...\n";

    if (SUCCEEDED(SimConnect_Open(&hSimConnect, "TelemetryBridge", NULL, 0, 0, 0)))
    {
        cout << "Baglanti basarili! Veri akisi basliyor.\n";

        // Veri Tanimlari
        SimConnect_AddToDataDefinition(hSimConnect, DEF_TELEM, "VERTICAL SPEED", "Feet per minute", SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(hSimConnect, DEF_TELEM, "RADIO HEIGHT", "Feet", SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(hSimConnect, DEF_TELEM, "G FORCE", "G Force", SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(hSimConnect, DEF_TELEM, "SIM ON GROUND", "Bool", SIMCONNECT_DATATYPE_FLOAT64);

        // Veri Istegi
        SimConnect_RequestDataOnSimObject(hSimConnect, REQ_TELEM, DEF_TELEM, SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_PERIOD_SIM_FRAME);

        // Ana Dongu
        while (quit == 0)
        {
            SimConnect_CallDispatch(hSimConnect, DispatchHandler, NULL);
            Sleep(1);
        }

        SimConnect_Close(hSimConnect);
    }
    else
    {
        cout << "HATA: Flight Simulator bulunamadi. Lutfen sim'i acip tekrar deneyin.\n";
        system("PAUSE");
    }

    return 0;
}
