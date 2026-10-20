#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "NexusBiteSettings.generated.h"

UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "NexusBite Hub Settings"))
class APPLICATIONDEFAULT_API UNexusBiteSettings : public UDeveloperSettings
{
    GENERATED_BODY()

public:
    // Se o servidor deve iniciar automaticamente no modo Shipping
    UPROPERTY(Config, EditAnywhere, Category = "Server", meta = (DisplayName = "Auto Start Server in Shipping"))
    bool bAutoStartServer = true;

    // Endere? de Bind (Padr? 127.0.0.1 para seguran?)
    UPROPERTY(Config, EditAnywhere, Category = "Server", meta = (DisplayName = "Server Bind Address"))
    FString ServerBindAddress = TEXT("127.0.0.1");

    // Porta do servidor RPC
    UPROPERTY(Config, EditAnywhere, Category = "Server", meta = (DisplayName = "Server Port"))
    int32 ServerPort = 30010;
};