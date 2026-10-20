#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "NexusBiteGameInstance.generated.h"

UCLASS()
class APPLICATIONDEFAULT_API UNexusBiteGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	// DECLARA?O: Esta linha avisa ao compilador que o construtor existe
	UNexusBiteGameInstance();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NexusBite | Remote Control")
	TObjectPtr<UObject> RemoteControlPresetReference;
};