#include "NexusBiteGameInstance.h"
#include "NexusBiteSettings.h" // Inclua o novo arquivo de configura?es
#include "Misc/CommandLine.h"
#include "HAL/IConsoleManager.h"

UNexusBiteGameInstance::UNexusBiteGameInstance()
{
    // Obt? a inst?cia das configura?es que voc?definiu no Editor
    const UNexusBiteSettings* HubSettings = GetDefault<UNexusBiteSettings>();

    if (HubSettings && HubSettings->bAutoStartServer)
    {
        // 1. Inje?o de Argumentos
        FString CurrentCmd = FCommandLine::Get();
        if (!CurrentCmd.Contains(TEXT("-RCWebControlEnable")))
        {
            FString MyArgs = TEXT(" -RCWebControlEnable -messaging");
            FCommandLine::Append(*MyArgs);
        }

        // 2. Aplica?o do Bind Address e Porta via CVars
        // Usamos ECVF_SetByCode para garantir que a UI do Project Settings ven? qualquer trava do Shipping
        if (IConsoleVariable* BindVar = IConsoleManager::Get().FindConsoleVariable(TEXT("WebControl.ServerBindAddress")))
        {
            BindVar->Set(*HubSettings->ServerBindAddress, ECVF_SetByCode);
        }

        if (IConsoleVariable* PortVar = IConsoleManager::Get().FindConsoleVariable(TEXT("WebControl.ServerPort")))
        {
            PortVar->Set(HubSettings->ServerPort, ECVF_SetByCode);
        }

        UE_LOG(LogTemp, Log, TEXT("NexusBite: Servidor configurado via Project Settings."));
    }
}